from . import ast


class IRGenerator:
    """Converts the AST to Three-Address Code (TAC) lines."""

    def __init__(self):
        self._temp  = 0
        self._label = 0
        self.lines  = []

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _new_temp(self):
        self._temp += 1
        return f"t{self._temp}"

    def _new_label(self):
        self._label += 1
        return f"L{self._label}"

    def _emit(self, text):
        self.lines.append(text)

    # ── Entry point ─────────────────────────────────────────────────────────

    def generate(self, program):
        for stmt in program.statements:
            self._gen_stmt(stmt)
        return self.lines

    # ── Statements ──────────────────────────────────────────────────────────

    def _gen_stmt(self, node):

        if isinstance(node, ast.VarDecl):
            val = self._gen_expr(node.initializer) if node.initializer else "0"
            self._emit(f"{node.name} = {val}")

        elif isinstance(node, ast.Assignment):
            self._emit(f"{node.name} = {self._gen_expr(node.value)}")

        elif isinstance(node, ast.UpdateStmt):
            self._emit(f"{node.name} = {node.name} {node.op} 1")

        elif isinstance(node, ast.CoutStmt):
            for val in node.values:
                self._emit(f"cout {self._gen_expr(val)}")

        elif isinstance(node, ast.IfStmt):
            cond       = self._gen_expr(node.condition)
            else_lbl   = self._new_label()
            end_lbl    = self._new_label()
            self._emit(f"ifFalse {cond} goto {else_lbl}")
            self._gen_block(node.then_block)
            self._emit(f"goto {end_lbl}")
            self._emit(f"{else_lbl}:")
            if node.else_block:
                self._gen_block(node.else_block)
            self._emit(f"{end_lbl}:")

        elif isinstance(node, ast.WhileStmt):
            start = self._new_label()
            end   = self._new_label()
            self._emit(f"{start}:")
            self._emit(f"ifFalse {self._gen_expr(node.condition)} goto {end}")
            self._gen_block(node.body)
            self._emit(f"goto {start}")
            self._emit(f"{end}:")

        elif isinstance(node, ast.DoWhileStmt):
            start = self._new_label()
            end   = self._new_label()
            self._emit(f"{start}:")
            self._gen_block(node.body)
            self._emit(f"ifFalse {self._gen_expr(node.condition)} goto {end}")
            self._emit(f"goto {start}")
            self._emit(f"{end}:")

        elif isinstance(node, ast.ForStmt):
            self._gen_stmt(node.init)
            start = self._new_label()
            end   = self._new_label()
            self._emit(f"{start}:")
            self._emit(f"ifFalse {self._gen_expr(node.condition)} goto {end}")
            self._gen_block(node.body)
            self._gen_stmt(node.update)
            self._emit(f"goto {start}")
            self._emit(f"{end}:")

    def _gen_block(self, block):
        for stmt in block.statements:
            self._gen_stmt(stmt)

    # ── Expressions ─────────────────────────────────────────────────────────

    def _gen_expr(self, node):

        if isinstance(node, ast.Literal):
            if node.type_name == "bool":
                return "true" if node.value else "false"
            return str(node.value)

        if isinstance(node, ast.Identifier):
            return node.name

        if isinstance(node, ast.UnaryOp):
            val  = self._gen_expr(node.operand)
            tmp  = self._new_temp()
            self._emit(f"{tmp} = {node.op}{val}")
            return tmp

        if isinstance(node, ast.BinaryOp):
            left  = self._gen_expr(node.left)
            right = self._gen_expr(node.right)
            tmp   = self._new_temp()
            self._emit(f"{tmp} = {left} {node.op} {right}")
            return tmp

        raise ValueError(f"Unknown AST node: {type(node).__name__}")
