import streamlit as st
import os
import zipfile
import google.generativeai as genai
import datetime

# Gemini API setup
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="Gemini AI Code Assistant", layout="wide")
st.title("💡 Gemini AI Code Assistant")

# Sidebar - File Upload
st.sidebar.header("📂 Upload Code File or Project ZIP")
uploaded_file = st.sidebar.file_uploader("Upload .zip or code file", type=["zip", "py", "java", "cpp", "js", "ts", "html", "css"])

code_files = {}

# Process uploaded file
if uploaded_file:
    if uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
            zip_ref.extractall("temp_code")
            for root, dirs, files in os.walk("temp_code"):
                for file in files:
                    path = os.path.join(root, file)
                    if file.endswith((".py", ".java", ".cpp", ".js", ".ts", ".html", ".css")):
                        rel_path = os.path.relpath(path, "temp_code")
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            code_files[rel_path] = f.read()
    else:
        file_content = uploaded_file.read().decode("utf-8")
        code_files[uploaded_file.name] = file_content

if code_files:
    file_name = st.sidebar.selectbox("📄 Select a file", list(code_files.keys()))
    code = code_files[file_name]
    st.code(code, language=file_name.split(".")[-1])

    # Tabs
    tabs = st.tabs(["💬 Chat Assistant", "🧠 Prompt Templates", "📋 Paste & Ask", "🔧 Smart Actions", "📄 Other Tools"])
    combined_code = "\n".join(f"--- {fname} ---\n{content}" for fname, content in code_files.items())

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat Assistant Tab
    with tabs[0]:
        st.subheader("Chat with Gemini about your codebase")
        for msg in st.session_state.messages:
            st.markdown(f"**{'You' if msg['role'] == 'user' else 'Gemini'}:** {msg['content']}")

        user_input = st.chat_input("Ask something about your code...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            full_prompt = f"You are a code assistant. The codebase includes multiple files:\n\n{combined_code}\n\nUser asked:\n{user_input}"
            gemini_response = model.generate_content(full_prompt).text
            st.session_state.messages.append({"role": "gemini", "content": gemini_response})
            st.experimental_rerun()

    # Prompt Templates
    with tabs[1]:
        st.subheader("🎯 Prompt Templates")
        template = st.selectbox("Choose a prompt", [
            "Explain the selected file",
            "Summarize this file",
            "Identify bugs or risks",
            "Suggest performance improvements",
            "Convert to async (if applicable)",
            "Suggest better naming conventions",
        ])
        if st.button("Run Template Prompt"):
            prompt_map = {
                "Explain the selected file": f"Explain this code:\n\n{code}",
                "Summarize this file": f"Give a detailed summary of this file:\n\n{code}",
                "Identify bugs or risks": f"Find bugs or logical errors in this code:\n\n{code}",
                "Suggest performance improvements": f"Suggest performance improvements:\n\n{code}",
                "Convert to async (if applicable)": f"Convert this code to async (if applicable):\n\n{code}",
                "Suggest better naming conventions": f"Suggest better variable/function/class names for readability:\n\n{code}",
            }
            response = model.generate_content(prompt_map[template]).text
            st.code(response)
            st.download_button("💾 Download Response", data=response, file_name="gemini_response.txt")

    # Paste & Ask
    with tabs[2]:
        st.subheader("📝 Paste your code snippet below")
        pasted_code = st.text_area("Paste any code (Python, Java, etc.)")
        pasted_prompt = st.text_input("What do you want Gemini to do with it?")
        if st.button("💬 Run on Pasted Code"):
            full_prompt = f"Here is some code:\n{pasted_code}\n\nInstruction: {pasted_prompt}"
            response = model.generate_content(full_prompt).text
            st.code(response)
            st.download_button("💾 Download Gemini's Response", response, file_name="code_assistant_reply.txt")

    # Smart Actions
    with tabs[3]:
        st.subheader("⚡ Smart Actions for selected file")
        if st.button("📌 Explain Code"):
            prompt = f"Explain the following code:\n\n{code}"
            response = model.generate_content(prompt).text
            st.success(response)
        if st.button("🛠️ Suggest Improvements"):
            prompt = f"Suggest improvements for this code:\n\n{code}"
            response = model.generate_content(prompt).text
            st.code(response)
        if st.button("🐛 Find Bugs"):
            prompt = f"Detect bugs or logical issues in this code:\n\n{code}"
            response = model.generate_content(prompt).text
            st.warning(response)
        if st.button("📋 Show Time & Space Complexity"):
            prompt = f"Analyze the time and space complexity of this code:\n\n{code}"
            response = model.generate_content(prompt).text
            st.info(response)

    # Other Tools (refactor, test gen, smells, translate)
    with tabs[4]:
        sub_tabs = st.tabs(["Refactor", "Generate Tests", "Docstrings", "Smells", "Translate"])
        with sub_tabs[0]:
            if st.button("🔧 Refactor"):
                response = model.generate_content(f"Refactor this code:\n\n{code}").text
                st.code(response)
        with sub_tabs[1]:
            if st.button("🧪 Generate Tests"):
                response = model.generate_content(f"Write unit tests for:\n\n{code}").text
                st.code(response)
        with sub_tabs[2]:
            if st.button("📘 Add Docstrings"):
                response = model.generate_content(f"Add docstrings and inline comments:\n\n{code}").text
                st.code(response)
        with sub_tabs[3]:
            if st.button("🐞 Code Smells"):
                response = model.generate_content(f"Identify code smells in:\n\n{code}").text
                st.warning(response)
        with sub_tabs[4]:
            target = st.selectbox("Translate to:", ["Java", "Python", "C++", "JavaScript"])
            if st.button("🌍 Translate"):
                prompt = f"Translate this code to {target}:\n\n{code}"
                response = model.generate_content(prompt).text
                st.code(response)

else:
    st.info("Please upload a .zip file or code file to get started.")
