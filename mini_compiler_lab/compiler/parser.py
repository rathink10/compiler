from .lexer import Token
from . import ast


class ParseError(Exception):
    def __init__(self, message, token: Token):
        super().__init__(message)
        self.message = message
        self.token   = token


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    # ── Helpers ─────────────────────────────────────────────────────────────

    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.current()
        self.pos += 1
        return tok

    def check(self, kind):
        return self.current().kind == kind

    def match(self, *kinds):
        if self.current().kind in kinds:
            return self.advance()
        return None

    def expect(self, kind, message=None):
        if not self.check(kind):
            tok = self.current()
            raise ParseError(
                message or f"Expected {kind}, found '{tok.value or tok.kind}'", tok
            )
        return self.advance()

    # ── Entry point ─────────────────────────────────────────────────────────

    def parse(self):
        stmts = []
        while not self.check("EOF"):
            stmts.append(self.statement())
        return ast.Program(stmts)

    # ── Statements ──────────────────────────────────────────────────────────

    def statement(self):
        if self.check("INT") or self.check("FLOAT") or self.check("BOOL") or self.check("STRING_TYPE"):
            return self.var_decl()
        if self.check("ID"):
            return self.assignment_or_update()
        if self.check("COUT"):
            return self.cout_stmt()
        if self.check("IF"):
            return self.if_stmt()
        if self.check("WHILE"):
            return self.while_stmt()
        if self.check("DO"):
            return self.do_while_stmt()
        if self.check("FOR"):
            return self.for_stmt()
        tok = self.current()
        raise ParseError(f"Unexpected token '{tok.value or tok.kind}'", tok)

    def var_decl(self):
        typ  = self.advance()
        name = self.expect("ID", "Expected variable name after type")
        init = self.expression() if self.match("ASSIGN") else None
        self.expect("SEMI", "Expected ';' after variable declaration")
        return ast.VarDecl(typ.value, name.value, init)

    def assignment_or_update(self):
        name = self.advance()

        # i++ / i--
        if self.match("INC"):
            self.expect("SEMI", "Expected ';' after '++'")
            return ast.UpdateStmt(name.value, "+")
        if self.match("DEC"):
            self.expect("SEMI", "Expected ';' after '--'")
            return ast.UpdateStmt(name.value, "-")

        # x = / x += / x -= / x *= / x /=
        if self.match("ASSIGN"):
            value = self.expression()
        elif self.match("PLUS_ASSIGN"):
            value = ast.BinaryOp(ast.Identifier(name.value), "+", self.expression())
        elif self.match("MINUS_ASSIGN"):
            value = ast.BinaryOp(ast.Identifier(name.value), "-", self.expression())
        elif self.match("MUL_ASSIGN"):
            value = ast.BinaryOp(ast.Identifier(name.value), "*", self.expression())
        elif self.match("DIV_ASSIGN"):
            value = ast.BinaryOp(ast.Identifier(name.value), "/", self.expression())
        else:
            raise ParseError("Expected assignment operator", self.current())

        self.expect("SEMI", "Expected ';' after assignment")
        return ast.Assignment(name.value, value)

    def cout_stmt(self):
        self.advance()
        values = []
        while True:
            self.expect("LSHIFT", "Expected '<<' after cout")
            values.append(self.expression())
            if not self.check("LSHIFT"):
                break
        self.expect("SEMI", "Expected ';' after cout")
        return ast.CoutStmt(values)

    def if_stmt(self):
        self.advance()
        self.expect("LPAREN", "Expected '(' after if")
        cond = self.expression()
        self.expect("RPAREN", "Expected ')' after if condition")
        then      = self.block()
        otherwise = self.block() if self.match("ELSE") else None
        return ast.IfStmt(cond, then, otherwise)

    def while_stmt(self):
        self.advance()
        self.expect("LPAREN", "Expected '(' after while")
        cond = self.expression()
        self.expect("RPAREN", "Expected ')' after while condition")
        return ast.WhileStmt(cond, self.block())

    def do_while_stmt(self):
        self.advance()
        body = self.block()
        self.expect("WHILE", "Expected 'while' after do block")
        self.expect("LPAREN", "Expected '(' after while")
        cond = self.expression()
        self.expect("RPAREN", "Expected ')' after condition")
        self.expect("SEMI", "Expected ';' after do-while")
        return ast.DoWhileStmt(body, cond)

    def for_stmt(self):
        self.advance()
        self.expect("LPAREN", "Expected '(' after for")

        # init: either a declaration or assignment
        if self.check("INT") or self.check("FLOAT") or self.check("BOOL") or self.check("STRING_TYPE"):
            init = self.var_decl()
        else:
            init = self.assignment_or_update()

        cond = self.expression()
        self.expect("SEMI", "Expected ';' after for condition")

        # update: only i++ / i-- is allowed in the for-header
        name = self.expect("ID", "Expected variable in for update")
        if self.match("INC"):
            update = ast.UpdateStmt(name.value, "+")
        elif self.match("DEC"):
            update = ast.UpdateStmt(name.value, "-")
        else:
            raise ParseError("Expected '++' or '--' in for update", self.current())

        self.expect("RPAREN", "Expected ')' after for update")
        return ast.ForStmt(init, cond, update, self.block())

    def block(self):
        self.expect("LBRACE", "Expected '{'")
        stmts = []
        while not self.check("RBRACE") and not self.check("EOF"):
            stmts.append(self.statement())
        self.expect("RBRACE", "Expected '}'")
        return ast.Block(stmts)

    # ── Expressions (recursive descent, operator precedence) ────────────────

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        node = self.logical_and()
        while self.match("OR"):
            node = ast.BinaryOp(node, "||", self.logical_and())
        return node

    def logical_and(self):
        node = self.equality()
        while self.match("AND"):
            node = ast.BinaryOp(node, "&&", self.equality())
        return node

    def equality(self):
        node = self.comparison()
        while True:
            if self.match("EQ"):
                node = ast.BinaryOp(node, "==", self.comparison())
            elif self.match("NE"):
                node = ast.BinaryOp(node, "!=", self.comparison())
            else:
                return node

    def comparison(self):
        node = self.term()
        while True:
            if self.match("LT"):
                node = ast.BinaryOp(node, "<", self.term())
            elif self.match("LE"):
                node = ast.BinaryOp(node, "<=", self.term())
            elif self.match("GT"):
                node = ast.BinaryOp(node, ">", self.term())
            elif self.match("GE"):
                node = ast.BinaryOp(node, ">=", self.term())
            else:
                return node

    def term(self):
        node = self.factor()
        while True:
            if self.match("PLUS"):
                node = ast.BinaryOp(node, "+", self.factor())
            elif self.match("MINUS"):
                node = ast.BinaryOp(node, "-", self.factor())
            else:
                return node

    def factor(self):
        node = self.unary()
        while True:
            if self.match("MUL"):
                node = ast.BinaryOp(node, "*", self.unary())
            elif self.match("DIV"):
                node = ast.BinaryOp(node, "/", self.unary())
            else:
                return node

    def unary(self):
        if self.match("NOT"):
            return ast.UnaryOp("!", self.unary())
        if self.match("MINUS"):
            return ast.UnaryOp("-", self.unary())
        return self.primary()

    def primary(self):
        tok = self.current()
        if self.match("NUMBER"):
            return ast.Literal(
                float(tok.value) if "." in tok.value else int(tok.value),
                "float" if "." in tok.value else "int"
            )
        if self.match("TRUE"):
            return ast.Literal(True, "bool")
        if self.match("FALSE"):
            return ast.Literal(False, "bool")
        if self.match("STRING"):
            return ast.Literal(tok.value, "string")
        if self.match("ID"):
            return ast.Identifier(tok.value)
        if self.match("LPAREN"):
            expr = self.expression()
            self.expect("RPAREN", "Expected ')' after expression")
            return expr
        raise ParseError(f"Expected expression, found '{tok.value or tok.kind}'", tok)
