import os
import re

from groq import Groq


def heuristic_fix(stage, error_text, source):

    suggestions = []

    error = error_text.lower()

    if "expected ';'" in error:
        suggestions.append(
            "Add a semicolon ';' at the end of the statement."
        )

    elif "expected ')'" in error:
        suggestions.append(
            "Add the missing closing ')'."
        )

    elif "expected '('" in error:
        suggestions.append(
            "Add '(' after the keyword or function name."
        )

    elif "expected '{'" in error:
        suggestions.append(
            "Add '{' to start the block."
        )

    elif "expected '}'" in error:
        suggestions.append(
            "Add the missing '}' to close the block."
        )

    elif "unsupported operator" in error:
        suggestions.append(
            "Replace the unsupported operator with a valid MiniC operator."
        )

    elif "unexpected character" in error:
        suggestions.append(
            "Remove the unsupported character."
        )

    elif "used before declaration" in error:
        suggestions.append(
            "Declare the variable before using it."
        )

    elif "cannot assign" in error:
        suggestions.append(
            "Make the variable type and assigned value compatible."
        )

    else:
        suggestions.append(
            "Fix the first compiler error and compile again."
        )

    return {
        "mode": "Built-in Compiler Assistant",

        "diagnosis": (
            "The "
            + stage
            + " stage detected this error:\n\n"
            + error_text
        ),

        "suggestions": suggestions,

        "corrected_code": None
    }


def extract_corrected_code(text):

    matches = re.findall(
        r"```(?:c|cpp|text)?\s*(.*?)```",
        text,
        re.DOTALL
    )

    if matches:
        return matches[-1].strip()

    return None


def groq_fix(stage, error_text, source):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    try:

        client = Groq(
            api_key=api_key
        )

        model = os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile"
        )

        prompt = (
            "You are an AI assistant inside a Compiler "
            "Visualization Lab.\n\n"

            "The student is learning compiler design.\n"

            "The language is a small C-like language called MiniC.\n\n"

            "Compiler stage that failed:\n"
            + stage
            + "\n\n"

            "Compiler error:\n"
            + error_text
            + "\n\n"

            "Student source code:\n"
            + source
            + "\n\n"

            "Explain the problem in beginner-friendly language.\n\n"

            "Your answer MUST contain these sections:\n\n"

            "WHAT HAPPENED\n"
            "Explain what the compiler detected.\n\n"

            "WHY THIS STAGE CAUGHT IT\n"
            "Explain why this belongs to "
            + stage
            + " instead of another compiler stage.\n\n"

            "WHAT IS WRONG\n"
            "Point to the specific problem in the code.\n\n"

            "HOW TO FIX IT\n"
            "Give the exact change the student should make.\n\n"

            "CORRECTED CODE\n"
            "Show the complete corrected MiniC program inside "
            "a code block.\n\n"

            "Do not introduce features that MiniC does not support."
        )

        response = client.chat.completions.create(

            model=model,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a compiler-design teaching assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            max_completion_tokens=1200
        )

        answer = response.choices[0].message.content

        corrected = extract_corrected_code(
            answer
        )

        return {
            "mode": "Groq AI",

            "diagnosis": answer,

            "suggestions": [
                "Apply the correction shown by the AI and compile again."
            ],

            "corrected_code": corrected
        }

    except Exception as exc:

        fallback = heuristic_fix(
            stage,
            error_text,
            source
        )

        fallback["mode"] = (
            "Built-in fallback "
            "(Groq unavailable: "
            + type(exc).__name__
            + ")"
        )

        return fallback


def explain_error(stage, error_text, source):

    result = groq_fix(
        stage,
        error_text,
        source
    )

    if result is not None:
        return result

    return heuristic_fix(
        stage,
        error_text,
        source
    )
