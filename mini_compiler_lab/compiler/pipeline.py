from dataclasses import dataclass
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .ir import IRGenerator
from .optimizer import optimize
from .codegen import generate_assembly
from .ai_assistant import explain_error

@dataclass
class StageResult:
    name: str
    ok: bool
    output: object = None
    error: str = ""
    ai: dict = None

def compile_source(source: str):
    results = []
    try:
        tokens = Lexer(source).tokenize()
        results.append(StageResult("1. Lexical Analysis", True, [
            {"kind": t.kind, "value": t.value, "line": t.line, "column": t.column} for t in tokens
        ]))
    except Exception as exc:
        msg = getattr(exc, "message", str(exc))
        results.append(StageResult("1. Lexical Analysis", False, error=msg, ai=explain_error("Lexical Analysis", msg, source)))
        return results

    try:
        program = Parser(tokens).parse()
        results.append(StageResult("2. Syntax Analysis", True, program))
    except Exception as exc:
        msg = getattr(exc, "message", str(exc))
        results.append(StageResult("2. Syntax Analysis", False, error=msg, ai=explain_error("Syntax Analysis", msg, source)))
        return results

    try:
        symbols = SemanticAnalyzer().analyze(program)
        results.append(StageResult("3. Semantic Analysis", True, symbols))
    except Exception as exc:
        msg = getattr(exc, "message", str(exc))
        results.append(StageResult("3. Semantic Analysis", False, error=msg, ai=explain_error("Semantic Analysis", msg, source)))
        return results

    try:
        ir = IRGenerator().generate(program)
        results.append(StageResult("4. Intermediate Code (Three-Address)", True, ir))
    except Exception as exc:
        msg = str(exc)
        results.append(StageResult("4. Intermediate Code (Three-Address)", False, error=msg, ai=explain_error("Intermediate Code Generation", msg, source)))
        return results

    try:
        optimized, changes = optimize(ir)
        results.append(StageResult("5. Code Optimization", True, {"before": ir, "after": optimized, "changes": changes}))
    except Exception as exc:
        msg = str(exc)
        results.append(StageResult("5. Code Optimization", False, error=msg, ai=explain_error("Code Optimization", msg, source)))
        return results

    try:
        asm = generate_assembly(optimized)
        results.append(StageResult("6. Target Code Generation", True, asm))
    except Exception as exc:
        msg = str(exc)
        results.append(StageResult("6. Target Code Generation", False, error=msg, ai=explain_error("Target Code Generation", msg, source)))
        return results
    return results
