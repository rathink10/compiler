import re

def _literal(v):
    if v in ("true", "false"): return v
    try: return float(v) if "." in v else int(v)
    except ValueError: return None

def _fmt(v):
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    return str(v)

def optimize(lines):
    out, env, changes = [], {}, []
    bin_re = re.compile(r"^(\w+)\s*=\s*([-\w.]+)\s*([+\-*/<>]=?|==|!=|&&|\|\|)\s*([-\w.]+)$")
    assign_re = re.compile(r"^(\w+)\s*=\s*(.+)$")
    for line in lines:
        m = bin_re.match(line)
        if m:
            target, a, op, b = m.groups()
            av, bv = env.get(a, _literal(a)), env.get(b, _literal(b))
            if av is not None and bv is not None:
                try:
                    result = {
                        "+": lambda: av + bv, "-": lambda: av - bv, "*": lambda: av * bv,
                        "/": lambda: av / bv, "<": lambda: av < bv, "<=": lambda: av <= bv,
                        ">": lambda: av > bv, ">=": lambda: av >= bv, "==": lambda: av == bv,
                        "!=": lambda: av != bv, "&&": lambda: bool(av) and bool(bv),
                        "||": lambda: bool(av) or bool(bv),
                    }[op]()
                    text = _fmt(result)
                    out.append(f"{target} = {text}"); env[target] = result
                    changes.append(f"Constant folding: {line} → {target} = {text}")
                    continue
                except Exception:
                    pass
        if m := assign_re.match(line):
            target, rhs = m.groups()
            lit = _literal(rhs)
            if lit is not None: env[target] = lit
            elif rhs in env: env[target] = env[rhs]
            else: env.pop(target, None)
        out.append(line)

    simple = []
    for line in out:
        m = bin_re.match(line)
        if m:
            target, a, op, b = m.groups()
            repl = None
            if op == "+" and b == "0": repl = a
            elif op == "+" and a == "0": repl = b
            elif op == "*" and b == "1": repl = a
            elif op == "*" and a == "1": repl = b
            if repl is not None:
                simple.append(f"{target} = {repl}")
                changes.append(f"Algebraic simplification: {line} → {target} = {repl}")
                continue
        simple.append(line)
    return simple, changes
