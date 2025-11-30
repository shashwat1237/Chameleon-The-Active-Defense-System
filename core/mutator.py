# core/mutator.py (REPLACE)
import ast
import secrets
import string
import os
import json
import traceback

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "target_app", "template.py")

# local project output (best-effort, not required on Render)
PROJECT_OUTPUT_PATH = os.path.join(BASE_DIR, "target_app", "active_server.py")
# runtime (Render-safe) output
RUNTIME_OUTPUT_PATH = "/tmp/active_server.py"
STATE_PATH = "/tmp/mutation_state.json"

def generate_chaos_string(length=6):
    chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

class ChaosTransformer(ast.NodeTransformer):
    def __init__(self):
        self.route_map = {}

    def visit_FunctionDef(self, node):
        if not node.decorator_list:
            return node

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and hasattr(decorator.func, 'attr'):
                if decorator.func.attr in ['get', 'post', 'put', 'delete']:
                    if decorator.args and hasattr(decorator.args[0], 'value'):
                        original_path = decorator.args[0].value

                        if original_path == "/":
                            self.route_map[original_path] = original_path
                            return node

                        mutation_hash = generate_chaos_string()
                        new_path = f"{original_path}_{mutation_hash}"
                        new_func_name = f"{node.name}_{mutation_hash}"

                        self.route_map[original_path] = new_path

                        decorator.args[0].value = new_path
                        node.name = new_func_name

        return node

def run_mutation():
    if not os.path.exists(TEMPLATE_PATH):
        print(f"[MUTATOR][ERROR] Template not found at {TEMPLATE_PATH}")
        return {}

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as src:
        tree = ast.parse(src.read())

    transformer = ChaosTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    mutated_source = ast.unparse(new_tree)

    # Best-effort: write project file (useful locally)
    try:
        with open(PROJECT_OUTPUT_PATH, "w", encoding="utf-8") as dst:
            dst.write(mutated_source)
        print(f"[MUTATOR] Wrote local project output -> {PROJECT_OUTPUT_PATH}")
    except Exception as e:
        print(f"[MUTATOR] Local write skipped: {e}")

    # Write runtime mutated server to /tmp so Render + nodes can import it
    try:
        with open(RUNTIME_OUTPUT_PATH, "w", encoding="utf-8") as dst:
            dst.write(mutated_source)
        print(f"[MUTATOR] Wrote runtime output -> {RUNTIME_OUTPUT_PATH}")
    except Exception as e:
        print(f"[MUTATOR][ERROR] Failed to write runtime output: {e}")
        print(traceback.format_exc())

    # Save route map to Render-safe path
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(transformer.route_map, f, indent=4)
        print(f"[MUTATOR] State saved -> {STATE_PATH}")
    except Exception as e:
        print(f"[MUTATOR][ERROR] Failed writing state: {e}")
        print(traceback.format_exc())

    return transformer.route_map

if __name__ == "__main__":
    print(run_mutation())
