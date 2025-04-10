import streamlit as st
import os
import zipfile
import google.generativeai as genai

# Setup Gemini
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

    # Chat Assistant tab
    chat_tab, *other_tabs = st.tabs([
        "💬 Chat Assistant", "🔍 Code Review", "🔧 Refactor", "🧪 Tests",
        "📘 Docstrings", "🔐 Security", "🐞 Smells", "🌐 Translate", "🧠 Learning", "📄 Summary"
    ])

    with chat_tab:
        st.subheader("Chat with Gemini About Your Codebase")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Combine all files into a single context
        combined_code = ""
        for fname, content in code_files.items():
            combined_code += f"--- FILE: {fname} ---\n{content}\n"

        # Display chat history
        for msg in st.session_state.messages:
            role, content = msg["role"], msg["content"]
            if role == "user":
                st.markdown(f"🧑‍💻 **You:** {content}")
            else:
                st.markdown(f"🤖 **Gemini:** {content}")

        user_input = st.chat_input("Type your question about the codebase here...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            full_prompt = f"You are a helpful AI assistant. The user uploaded a multi-file codebase:\n\n{combined_code}\n\nThey asked:\n{user_input}"
            gemini_response = model.generate_content(full_prompt).text
            st.session_state.messages.append({"role": "gemini", "content": gemini_response})
            st.experimental_rerun()

    with other_tabs[0]:
        st.subheader("Ask Gemini About the Code")
        user_question = st.text_area("❓ Enter your question", key="qa")
        if st.button("💬 Ask Gemini"):
            response = model.generate_content(f"{user_question}\n\nCode:\n{code}")
            st.success(response.text)

    with other_tabs[1]:
        st.subheader("Refactor Code")
        if st.button("🛠️ Refactor this code"):
            prompt = f"Refactor this code for better performance and readability:\n\n{code}"
            response = model.generate_content(prompt)
            st.code(response.text, language=file_name.split(".")[-1])

    with other_tabs[2]:
        st.subheader("Generate Unit Tests")
        if st.button("🧪 Generate Tests"):
            prompt = f"Write unit tests for the following code:\n\n{code}"
            response = model.generate_content(prompt)
            st.code(response.text)

    with other_tabs[3]:
        st.subheader("Add Docstrings and Comments")
        if st.button("📘 Add Docstrings"):
            prompt = f"Add Python-style docstrings and inline comments to the following code:\n\n{code}"
            response = model.generate_content(prompt)
            st.code(response.text)

    with other_tabs[4]:
        st.subheader("Security Audit")
        if st.button("🔐 Check for Vulnerabilities"):
            prompt = f"Analyze this code and highlight any security vulnerabilities or risks:\n\n{code}"
            response = model.generate_content(prompt)
            st.warning(response.text)

    with other_tabs[5]:
        st.subheader("Code Smell Detection")
        if st.button("🐞 Find Code Smells"):
            prompt = f"Review this code for code smells, bad practices, and areas to improve:\n\n{code}"
            response = model.generate_content(prompt)
            st.info(response.text)

    with other_tabs[6]:
        st.subheader("Translate Code to Another Language")
        target_lang = st.selectbox("Translate to:", ["Java", "Python", "C++", "JavaScript"])
        if st.button("🌐 Translate Code"):
            prompt = f"Translate this code to {target_lang}:\n\n{code}"
            response = model.generate_content(prompt)
            st.code(response.text, language=target_lang.lower())

    with other_tabs[7]:
        st.subheader("Learning Suggestions")
        if st.button("🧠 Get Learning Tips"):
            prompt = f"Suggest learning resources and improvements for a developer who wrote this code:\n\n{code}"
            response = model.generate_content(prompt)
            st.success(response.text)

    with other_tabs[8]:
        st.subheader("Project/File Summary")
        if st.button("📄 Summarize this file"):
            prompt = f"Summarize what this code does and how it works:\n\n{code}"
            response = model.generate_content(prompt)
            st.markdown(response.text)
else:
    st.info("Please upload a .zip file or code file to get started.")
