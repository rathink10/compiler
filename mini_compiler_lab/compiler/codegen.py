import re


def generate_assembly(lines):
    """Convert Three-Address Code lines into educational pseudo-assembly."""

    asm = [
        "; ===== Mini C++ Compiler — Target Code =====",
        "; Educational pseudo-assembly",
    ]

    for line in lines:

        # Label
        if line.endswith(":"):
            asm.append(line)

        # Conditional jump:  ifFalse <cond> goto <label>
        elif line.startswith("ifFalse "):
            _, cond, _, label = line.split()
            asm += [f"LOAD {cond}", f"JZ {label}"]

        # Unconditional jump:  goto <label>
        elif line.startswith("goto "):
            asm.append(f"JMP {line.split()[1]}")

        # Print:  cout <value>
        elif line.startswith("cout "):
            asm.append(f"PRINT {line[5:]}")

        # Assignment:  target = rhs
        else:
            m = re.match(r"^(\w+)\s*=\s*(.+)$", line)
            if not m:
                asm.append(f"; {line}")
                continue

            target, rhs = m.group(1), m.group(2)

            # Unary:  = -val  or  = !val
            u = re.match(r"^([!\-])(.+)$", rhs)
            if u:
                op, val = u.group(1), u.group(2)
                asm += [f"LOAD {val}", "NEG" if op == "-" else "NOT", f"STORE {target}"]
                continue

            # Binary:  = left OP right
            b = re.match(r"^(.+?)\s+([+\-*/\<\>]=?|==|!=|&&|\|\|)\s+(.+)$", rhs)
            if b:
                left, op, right = b.group(1), b.group(2), b.group(3)
                asm += [f"LOAD {left}", f"OP {op} {right}", f"STORE {target}"]
                continue

            # Simple copy:  = val
            asm += [f"LOAD {rhs}", f"STORE {target}"]

    return asm
