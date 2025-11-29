import ast
import secrets
import string
import os

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "target_app", "template.py")
OUTPUT_PATH = os.path.join(BASE_DIR, "target_app", "active_server.py")

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
    # [VERIFIED] Checks for template existence to prevent crashes
    if not os.path.exists(TEMPLATE_PATH):
        print(f"[ERROR] Template not found at {TEMPLATE_PATH}")
        return {}

    with open(TEMPLATE_PATH, "r") as source:
        tree = ast.parse(source.read())

    transformer = ChaosTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)

    with open(OUTPUT_PATH, "w") as dest:
        dest.write(ast.unparse(new_tree))
    
    return transformer.route_map

if __name__ == "__main__":
    print(run_mutation())