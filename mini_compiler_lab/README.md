# AI Compiler Lab

A submission-friendly mini compiler for a small C-like teaching language, **MiniC**.

## Compiler stages implemented

1. Lexical Analysis
2. Syntax Analysis
3. Semantic Analysis
4. Intermediate Code Generation (Three-Address Code)
5. Code Optimization
6. Target Code Generation (educational pseudo-assembly)

## AI feature

The app includes an AI Fix Assistant. It always works using built-in compiler-aware suggestions. When `OPENAI_API_KEY` is configured, it can additionally ask an OpenAI model for a clearer explanation and corrected snippet.

## Run

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Or on Windows, double-click `run_windows.bat` after installing the requirements.

## Optional real AI

PowerShell:

```powershell
$env:OPENAI_API_KEY="YOUR_KEY"
$env:OPENAI_MODEL="gpt-5-mini"
streamlit run app.py
```

The app still functions without the key.

## MiniC examples

Valid:

```c
int a = 10;
int b = 20;
int c;
c = a + b * 2;
print(c);
```

Syntax error:

```c
int a = 10
print(a);
```

Semantic error:

```c
int a;
b = 10;
```

Type error:

```c
bool flag;
flag = 10;
```

## Suggested lab description

"This project implements a miniature compiler pipeline for a C-like language. The lexer converts source characters into tokens. The recursive-descent parser validates grammar and constructs an AST. Semantic analysis checks declarations, types and valid operations through a symbol table. The compiler then produces three-address intermediate code, performs basic optimizations such as constant folding and algebraic simplification, and generates educational target pseudo-assembly. An AI Fix Assistant interprets compiler diagnostics and provides beginner-friendly repair suggestions."

## Important academic note

This is an educational compiler, not a production C/C++ compiler. Its supported grammar is intentionally small so that every compiler stage can be demonstrated clearly in a lab viva.
