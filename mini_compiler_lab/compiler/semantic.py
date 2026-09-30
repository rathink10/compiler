from . import ast


NUMERIC = {"int", "float"}


class SemanticError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class SemanticAnalyzer:

    def __init__(self):
        self.symbols = {}   # name -> type_name
        self.errors  = []

    def analyze(self, program):
        for stmt in program.statements:
            self.visit_stmt(stmt)
        if self.errors:
            raise SemanticError("\n".join(self.errors))
        return self.symbols

    # ── Statements ──────────────────────────────────────────────────────────

    def visit_stmt(self, node):

        if isinstance(node, ast.VarDecl):
            if node.name in self.symbols:
                self.errors.append(f"Variable '{node.name}' is already declared.")
                return
            if node.initializer:
                src = self.visit_expr(node.initializer)
                if not self._assignable(node.type_name, src):
                    self.errors.append(
                        f"Cannot assign {src} to {node.type_name} variable '{node.name}'."
                    )
            self.symbols[node.name] = node.type_name

        elif isinstance(node, ast.Assignment):
            if node.name not in self.symbols:
                self.errors.append(f"Variable '{node.name}' used before declaration.")
                self.visit_expr(node.value)
                return
            src = self.visit_expr(node.value)
            tgt = self.symbols[node.name]
            if not self._assignable(tgt, src):
                self.errors.append(f"Cannot assign {src} to {tgt} variable '{node.name}'.")

        elif isinstance(node, ast.UpdateStmt):
            if node.name not in self.symbols:
                self.errors.append(f"Variable '{node.name}' used before declaration.")
            elif self.symbols[node.name] not in NUMERIC:
                self.errors.append(f"Cannot increment/decrement non-numeric variable '{node.name}'.")

        elif isinstance(node, ast.CoutStmt):
            for val in node.values:
                self.visit_expr(val)

        elif isinstance(node, ast.IfStmt):
            if self.visit_expr(node.condition) != "bool":
                self.errors.append("If condition must be boolean.")
            self._visit_block(node.then_block)
            if node.else_block:
                self._visit_block(node.else_block)

        elif isinstance(node, ast.WhileStmt):
            if self.visit_expr(node.condition) != "bool":
                self.errors.append("While condition must be boolean.")
            self._visit_block(node.body)

        elif isinstance(node, ast.DoWhileStmt):
            self._visit_block(node.body)
            if self.visit_expr(node.condition) != "bool":
                self.errors.append("Do-while condition must be boolean.")

        elif isinstance(node, ast.ForStmt):
            self.visit_stmt(node.init)
            if self.visit_expr(node.condition) != "bool":
                self.errors.append("For condition must be boolean.")
            self.visit_stmt(node.update)
            self._visit_block(node.body)

    def _visit_block(self, block):
        for stmt in block.statements:
            self.visit_stmt(stmt)

    # ── Expressions ─────────────────────────────────────────────────────────

    def visit_expr(self, node):

        if isinstance(node, ast.Literal):
            return node.type_name

        if isinstance(node, ast.Identifier):
            if node.name not in self.symbols:
                self.errors.append(f"Variable '{node.name}' used before declaration.")
                return "error"
            return self.symbols[node.name]

        if isinstance(node, ast.UnaryOp):
            t = self.visit_expr(node.operand)
            if node.op == "!" and t != "bool":
                self.errors.append("Operator '!' requires a boolean operand.")
                return "error"
            if node.op == "-" and t not in NUMERIC:
                self.errors.append("Unary '-' requires a numeric operand.")
                return "error"
            return "bool" if node.op == "!" else t

        if isinstance(node, ast.BinaryOp):
            lt = self.visit_expr(node.left)
            rt = self.visit_expr(node.right)

            if node.op in {"+", "-", "*", "/"}:
                if lt in NUMERIC and rt in NUMERIC:
                    return "float" if "float" in (lt, rt) else "int"
                if node.op == "+" and lt == "string" and rt == "string":
                    return "string"
                self.errors.append(f"Operator '{node.op}' requires numeric operands.")
                return "error"

            if node.op in {"<", "<=", ">", ">="}:
                if lt in NUMERIC and rt in NUMERIC:
                    return "bool"
                self.errors.append(f"Comparison '{node.op}' requires numeric operands.")
                return "error"

            if node.op in {"==", "!="}:
                if lt not in ("error", rt) and rt != "error":
                    self.errors.append("Equality operands must have compatible types.")
                    return "error"
                return "bool"

            if node.op in {"&&", "||"}:
                if lt == "bool" and rt == "bool":
                    return "bool"
                self.errors.append(f"Logical operator '{node.op}' requires boolean operands.")
                return "error"

        return "error"

    # ── Helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _assignable(target, source):
        return (
            target == source
            or (target == "float" and source == "int")
        )
