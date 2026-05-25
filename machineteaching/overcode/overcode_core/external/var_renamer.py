import ast


class IdentifierRenamer(ast.NodeTransformer):
    def visit_Name(self, node):
        # Check if the identifier name is in the mapping
        if node.id in self.mapping:
            # Replace the identifier name with the new name
            node.id = self.mapping[node.id]
        return node

    def visit_arg(self, node):
        # Check if the argument name is in the mapping
        if node.arg in self.mapping:
            # Replace the argument name with the new name
            node.arg = self.mapping[node.arg]
        return node

    def visit_FunctionDef(self, node):
        # Check if the function name is in the mapping
        if node.name in self.mapping:
            # Replace the function name with the new name
            node.name = self.mapping[node.name]
        self.generic_visit(node)
        return node

    def visit_Attribute(self, node):
        # Check if the attribute name is in the mapping
        if node.attr in self.mapping:
            # Replace the attribute name with the new name
            node.attr = self.mapping[node.attr]
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        # Check if the class name is in the mapping
        if node.name in self.mapping:
            # Replace the class name with the new name
            node.name = self.mapping[node.name]
        self.generic_visit(node)
        return node

    def visit_Global(self, node):
        # Check if any of the global names are in the mapping
        node.names = [self.mapping.get(name, name) for name in node.names]
        return node

    def visit_Nonlocal(self, node):
        # Check if any of the nonlocal names are in the mapping
        node.names = [self.mapping.get(name, name) for name in node.names]
        return node


class VariableNameClashException(Exception):
    """Exception raised when a variable name change results in a clash
    with another variable which already has that name.

    Attributes:
        var_name -- the new variable name that resulted in the clash
        message -- explanation of the error
    """

    def __init__(self, var_name):
        self.var_name = var_name
        self.message = message = f"""Clash detected! Another variable 
                    in the source code already has the name '{self.var_name}'"""
        super().__init__(self.message)


# Making the rename method flexible
def rename_var(src_code: str, var_name: str, new_var_name: str) -> str:
    return ast_rename_var(src_code, var_name, new_var_name)


def ast_rename_var(src_code: str, var_name: str, new_var_name: str) -> str:
    # Parse the code into an AST
    tree = ast.parse(src_code)

    # Create a VariableRenamer object
    renamer = IdentifierRenamer()

    # Create a mapping of old variable names to new variable names
    mapping = {var_name: new_var_name}

    # Set the mapping on the renamer
    renamer.mapping = mapping

    # Use the renamer to transform the AST
    renamer.visit(tree)

    # Generate the new code from the transformed AST
    new_code = ast.unparse(tree)

    return new_code
