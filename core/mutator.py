import ast
import secrets
import string
import os
import json

# Resolve key project paths so the mutation engine always knows where the
# template lives and where the mutated server output should be written.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "target_app", "template.py")
OUTPUT_PATH = os.path.join(BASE_DIR, "target_app", "active_server.py")

def generate_chaos_string(length=6):
    # Creates a short random suffix used to mutate routes and function names.
    # Using secrets ensures cryptographic strength so collisions stay unlikely.
    chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

class ChaosTransformer(ast.NodeTransformer):
    # Walks the AST and applies mutations to all HTTP route decorators.
    # Builds a live mapping of old → new paths for the proxy to reference.
    def __init__(self):
        self.route_map = {} 

    def visit_FunctionDef(self, node):
        # Only mutate endpoints that actually have FastAPI-style decorators.
        if not node.decorator_list:
            return node

        for decorator in node.decorator_list:
            # Detect typical FastAPI methods: get/post/put/delete.
            if isinstance(decorator, ast.Call) and hasattr(decorator.func, 'attr'):
                if decorator.func.attr in ['get', 'post', 'put', 'delete']:
                    # Pull the literal string route from the decorator.
                    if decorator.args and hasattr(decorator.args[0], 'value'):
                        original_path = decorator.args[0].value
                        
                        # Keep root endpoint untouched so the dashboard health check stays stable.
                        if original_path == "/":
                            self.route_map[original_path] = original_path
                            return node

                        # Create a mutated version of both the route and the handler function.
                        mutation_hash = generate_chaos_string()
                        new_path = f"{original_path}_{mutation_hash}"
                        new_func_name = f"{node.name}_{mutation_hash}"

                        # Store mapping so the proxy knows which new path replaced which original.
                        self.route_map[original_path] = new_path

                        # Apply the new mutated values back into the AST.
                        decorator.args[0].value = new_path
                        node.name = new_func_name
        
        return node

def run_mutation():
    # Ensure the template exists so we don’t mutate against a missing file,
    # which would otherwise crash and leave the system in an inconsistent state.
    if not os.path.exists(TEMPLATE_PATH):
        print(f"[ERROR] Template not found at {TEMPLATE_PATH}")
        return {}

    with open(TEMPLATE_PATH, "r") as source:
        tree = ast.parse(source.read())

    # Apply all transformations in one pass and clean up the AST afterwards.
    transformer = ChaosTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)

    # Write out the newly mutated server file that the active node will run.
    with open(OUTPUT_PATH, "w") as dest:
        dest.write(ast.unparse(new_tree))

    # SAVE ROUTE MAP TO JSON
    MUTATOR_DIR = os.path.dirname(os.path.abspath(__file__))
    CORE_DIR = os.path.abspath(os.path.join(MUTATOR_DIR, ".."))
    STATE_PATH = os.path.join(CORE_DIR, "mutation_state.json")
    with open(STATE_PATH, "w") as state_file:
        json.dump(transformer.route_map, state_file, indent=4)
    
    return transformer.route_map

if __name__ == "__main__":
    print(run_mutation())
