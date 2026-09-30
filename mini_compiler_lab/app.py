import json
import streamlit as st

from compiler.pipeline import compile_source


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI C++ Compiler Visualizer",
    page_icon="⚙️",
    layout="wide"
)


# ==========================================================
# DEFAULT C++ PROGRAM
# ==========================================================

DEFAULT_CODE = """int x = 10;
int y = x;
string s = "Hello C++";

if (y > 5) {
    cout << y;
} else {
    cout << 0;
}
"""


# ==========================================================
# ERROR DEMONSTRATION PROGRAMS
# ==========================================================

ERROR_PROGRAMS = {

    "Lexical Error — @": """int x = 10 @ 20;
cout << x;""",

    "Syntax Error — Missing ;": """int x = 10
cout << x;""",

    "Syntax Error — Missing )": """int x = 10;
if (x > 5 {
    cout << x;
}""",

    "Syntax Error — Missing }": """int x = 10;

if (x > 5) {
    cout << x;
""",

    "Semantic Error — Undeclared Variable": """int x;
y = 20;
cout << x;""",

    "Semantic Error — Wrong Type": """bool flag;
flag = 10;
cout << flag;""",
}


# ==========================================================
# SESSION STATE
# ==========================================================

if "source" not in st.session_state:
    st.session_state.source = DEFAULT_CODE

if "results" not in st.session_state:
    st.session_state.results = None


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("⚙️ Compiler Pipeline")

    st.write("✅ Lexical Analysis")
    st.write("✅ Syntax Analysis")
    st.write("✅ Semantic Analysis")
    st.write("✅ Intermediate Code")
    st.write("✅ Code Optimization")
    st.write("✅ Target Code Generation")

    st.divider()

    st.markdown("### 📚 Supported C++-like syntax")

    st.code(
        '''int x = 10;
int y = x;

cout << y;''',
        language="c"
    )

    st.write(
        "The compiler is implemented in Python, "
        "but the input language follows C++-style syntax."
    )


# ==========================================================
# HEADER
# ==========================================================

st.title("⚙️ AI C++ Compiler Visualizer")

st.caption(
    "Visualize how C++-like source code passes through "
    "the different phases of a compiler."
)


st.divider()


# ==========================================================
# SOURCE CODE
# ==========================================================

st.subheader("📝 Source Code")

st.text_area(
    "Enter your C++-like program below:",
    key="source",
    height=300
)


# ==========================================================
# ERROR LAB
# ==========================================================

st.subheader("🧪 Error Laboratory")

st.write(
    "Use these examples to demonstrate how different "
    "compiler stages detect different types of errors."
)


error_choice = st.selectbox(
    "Select an error example",
    list(ERROR_PROGRAMS.keys())
)


c1, c2 = st.columns(2)


with c1:

    if st.button(
        "Load Error Example",
        use_container_width=True
    ):

        st.session_state.source = ERROR_PROGRAMS[
            error_choice
        ]

        st.session_state.results = None

        st.rerun()


with c2:

    if st.button(
        "Reset Valid Program",
        use_container_width=True
    ):

        st.session_state.source = DEFAULT_CODE

        st.session_state.results = None

        st.rerun()


st.write("")


# ==========================================================
# COMPILE
# ==========================================================

if st.button(
    "🚀 Compile & Visualize",
    type="primary",
    use_container_width=True
):

    st.session_state.results = compile_source(
        st.session_state.source
    )


results = st.session_state.results


# ==========================================================
# RESULTS
# ==========================================================

if results:

    # ======================================================
    # COMPILATION JOURNEY
    # ======================================================

    st.divider()

    st.subheader("📊 Compilation Journey")

    failed_index = None

    for i, result in enumerate(results):

        if not result.ok:

            failed_index = i

            break


    journey = [
        "1. Lexical Analysis",
        "2. Syntax Analysis",
        "3. Semantic Analysis",
        "4. Intermediate Code",
        "5. Code Optimization",
        "6. Target Code Generation"
    ]


    for i, stage in enumerate(journey):

        if failed_index is None:

            if i < len(results):

                status = "✅ PASS"

            else:

                status = "⏳ NOT RUN"


        else:

            if i < failed_index:

                status = "✅ PASS"

            elif i == failed_index:

                status = "❌ FAILED"

            else:

                status = "⛔ NOT REACHED"


        col1, col2 = st.columns([5, 1])

        with col1:

            st.markdown(
                f"**{stage}**"
            )

        with col2:

            st.markdown(
                f"**{status}**"
            )


    # ======================================================
    # STAGE INSPECTOR
    # ======================================================

    st.divider()

    st.subheader("🔍 Compiler Stage Inspector")


    for result in results:

        # ==================================================
        # LEXICAL
        # ==================================================

        if result.name.startswith("1."):

            with st.expander(
                "✅ 1. Lexical Analysis",
                expanded=not result.ok
            ):

                st.markdown(
                    "### Characters → Tokens"
                )

                st.write(
                    """
                    The lexical analyzer reads the source
                    code character by character and converts
                    it into meaningful tokens.
                    """
                )


                if result.ok:

                    st.success(
                        "Lexical Analysis Successful"
                    )

                    st.write(
                        "Generated Tokens:"
                    )

                    st.dataframe(
                        result.output,
                        use_container_width=True
                    )

                else:

                    st.error(
                        "LEXICAL ERROR"
                    )

                    st.code(
                        result.error
                    )

                    st.info(
                        """
                        This error was caught during Lexical
                        Analysis because the input contains
                        an unsupported character or token.

                        Examples include:

                        • @
                        • <<
                        • >>
                        """
                    )


        # ==================================================
        # SYNTAX
        # ==================================================

        elif result.name.startswith("2."):

            with st.expander(
                "✅ 2. Syntax Analysis",
                expanded=not result.ok
            ):

                st.markdown(
                    "### Tokens → Abstract Syntax Tree"
                )

                st.write(
                    """
                    The syntax analyzer checks whether the
                    sequence of tokens follows the grammar
                    of the C++-like language.
                    """
                )


                if result.ok:

                    st.success(
                        "Syntax Analysis Successful"
                    )

                    st.write(
                        "Abstract Syntax Tree:"
                    )

                    st.code(
                        repr(result.output),
                        language="text"
                    )

                else:

                    st.error(
                        "SYNTAX ERROR"
                    )

                    st.code(
                        result.error
                    )

                    st.info(
                        """
                        The lexer recognized the individual
                        tokens successfully.

                        However, the arrangement of those
                        tokens does not follow the grammar.

                        Typical examples:

                        • Missing ;
                        • Missing )
                        • Missing }
                        • Incorrect statement structure
                        """
                    )


        # ==================================================
        # SEMANTIC
        # ==================================================

        elif result.name.startswith("3."):

            with st.expander(
                "✅ 3. Semantic Analysis",
                expanded=not result.ok
            ):

                st.markdown(
                    "### AST → Meaning + Type Checking"
                )

                st.write(
                    """
                    Semantic analysis checks whether the
                    program is meaningful according to
                    declarations and data types.
                    """
                )


                if result.ok:

                    st.success(
                        "Semantic Analysis Successful"
                    )

                    st.markdown(
                        "### 📚 Symbol Table"
                    )

                    st.json(
                        result.output
                    )

                else:

                    st.error(
                        "SEMANTIC ERROR"
                    )

                    st.code(
                        result.error
                    )

                    st.info(
                        """
                        The syntax is correct, but the
                        meaning of the program is invalid.

                        Examples:

                        • Variable used before declaration
                        • Incompatible assignment
                        • Wrong cout argument type
                        """
                    )


        # ==================================================
        # INTERMEDIATE CODE
        # ==================================================

        elif result.name.startswith("4."):

            with st.expander(
                "✅ 4. Intermediate Code",
                expanded=False
            ):

                st.markdown(
                    "### Three-Address Code"
                )

                st.write(
                    """
                    The compiler converts the program into
                    an intermediate representation that is
                    independent of a specific processor.
                    """
                )


                if result.ok:

                    st.code(
                        "\n".join(
                            result.output
                        ),
                        language="text"
                    )


        # ==================================================
        # OPTIMIZATION
        # ==================================================

        elif result.name.startswith("5."):

            with st.expander(
                "✅ 5. Code Optimization",
                expanded=False
            ):

                st.write(
                    """
                    The optimizer attempts to make the
                    intermediate code simpler or more efficient.
                    """
                )


                if result.ok:

                    st.markdown(
                        "### Before Optimization"
                    )

                    st.code(
                        "\n".join(
                            result.output["before"]
                        ),
                        language="text"
                    )


                    st.markdown(
                        "### After Optimization"
                    )

                    st.code(
                        "\n".join(
                            result.output["after"]
                        ),
                        language="text"
                    )


                    if result.output["changes"]:

                        st.markdown(
                            "### ⚡ Optimizations Performed"
                        )

                        for change in result.output["changes"]:

                            st.write(
                                "• " + change
                            )


        # ==================================================
        # TARGET CODE
        # ==================================================

        elif result.name.startswith("6."):

            with st.expander(
                "✅ 6. Target Code Generation",
                expanded=False
            ):

                st.markdown(
                    "### Target Pseudo-Assembly"
                )

                st.write(
                    """
                    The final compiler phase converts the
                    optimized intermediate representation
                    into target instructions.
                    """
                )


                if result.ok:

                    st.code(
                        "\n".join(
                            result.output
                        ),
                        language="asm"
                    )


    # ======================================================
    # AI ASSISTANT
    # ======================================================

    failed_result = next(
        (
            result
            for result in results
            if not result.ok
        ),
        None
    )


    if failed_result:

        st.divider()

        st.subheader(
            "🤖 AI Compiler Fix Assistant"
        )


        st.markdown(
            f"""
            ### Error caught at:

            **{failed_result.name}**
            """
        )


        st.error(
            failed_result.error
        )


        if failed_result.ai:

            st.markdown(
                "### 🧠 AI Explanation"
            )

            st.write(
                failed_result.ai.get(
                    "diagnosis",
                    ""
                )
            )


            suggestions = failed_result.ai.get(
                "suggestions",
                []
            )


            if suggestions:

                st.markdown(
                    "### 💡 Suggested Fix"
                )

                for suggestion in suggestions:

                    st.success(
                        suggestion
                    )


            corrected_code = failed_result.ai.get(
                "corrected_code"
            )


            if corrected_code:

                st.markdown(
                    "### ✅ Corrected Code"
                )

                st.code(
                    corrected_code,
                    language="c"
                )


        # ==================================================
        # WHY THIS STAGE?
        # ==================================================

        st.divider()

        st.subheader(
            "🎓 Why was this error caught at this stage?"
        )


        if failed_result.name.startswith("1."):

            st.info(
                """
                **Lexical Analysis**

                The lexer is responsible for converting
                characters into valid tokens.

                Therefore invalid characters and unsupported
                token patterns are detected here.
                """
            )


        elif failed_result.name.startswith("2."):

            st.info(
                """
                **Syntax Analysis**

                The lexer has already confirmed that the
                individual tokens are valid.

                The parser now checks whether those tokens
                follow the grammar.

                Therefore errors such as missing semicolons,
                parentheses or braces are detected here.
                """
            )


        elif failed_result.name.startswith("3."):

            st.info(
                """
                **Semantic Analysis**

                The program is grammatically correct, but
                its meaning is invalid.

                This stage detects undeclared variables,
                incompatible data types and invalid
                cout arguments.
                """
            )


    else:

        st.divider()

        st.success(
            "🎉 Compilation Successful!"
        )

        st.markdown(
            """
            The program successfully completed:

            **Lexical Analysis → Syntax Analysis →
            Semantic Analysis → Intermediate Code →
            Optimization → Target Code Generation**
            """
        )


    # ======================================================
    # REPORT
    # ======================================================

    st.divider()

    st.subheader(
        "📄 Compilation Report"
    )


    report = []


    for result in results:

        report.append(
            {
                "Stage": result.name,

                "Status": (
                    "PASS"
                    if result.ok
                    else "FAIL"
                ),

                "Error": result.error
            }
        )


    st.dataframe(
        report,
        use_container_width=True
    )


    st.download_button(
        "⬇️ Download Compilation Report",

        json.dumps(
            report,
            indent=2
        ),

        file_name="compiler_report.json",

        mime="application/json",

        use_container_width=True
    )
