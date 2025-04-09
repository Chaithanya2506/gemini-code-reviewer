import streamlit as st
import os
import zipfile
import tempfile
import google.generativeai as genai

# Load Gemini API key from Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

def extract_zip(zip_file):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

def get_code_files(directory):
    code_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.java', '.js', '.ts', '.cpp', '.c', '.cs', '.rb', '.go', '.php', '.html', '.css')):
                full_path = os.path.join(root, file)
                code_files.append(full_path)
    return code_files

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def ask_gemini(question, code):
    prompt = f"""
You are an AI code reviewer. Analyze the following code and answer the question below:

Code:
{code}

Question: {question}
"""
    response = model.generate_content(prompt)
    return response.text

def gemini_refactor(code):
    return model.generate_content(f"Refactor the following code:\n\n{code}").text

def gemini_generate_tests(code):
    return model.generate_content(f"Generate unit test cases for this code:\n\n{code}").text

def gemini_generate_docstrings(code):
    return model.generate_content(f"Add docstrings and inline comments:\n\n{code}").text

def gemini_security_audit(code):
    return model.generate_content(f"Review this code for security vulnerabilities:\n\n{code}").text

def gemini_generate_summary(code):
    return model.generate_content(f"Summarize the purpose and structure of this code:\n\n{code}").text

def gemini_explain_error(code, error):
    return model.generate_content(f"Explain the error:\n\nCode:\n{code}\n\nError:\n{error}").text

def gemini_translate_code(code, target_lang):
    return model.generate_content(f"Translate the following code into {target_lang}:\n\n{code}").text

def gemini_optimize_code(code):
    return model.generate_content(f"Optimize this code for performance and memory:\n\n{code}").text

def gemini_detect_skill_level(code):
    return model.generate_content(f"Assess the skill level of the author of this code:\n\n{code}").text

def gemini_suggest_learning(code):
    return model.generate_content(f"Suggest improvements or learning resources based on this code:\n\n{code}").text

def gemini_detect_code_smells(code):
    return model.generate_content(f"Detect any code smells in the following code:\n\n{code}").text

st.set_page_config(page_title="Gemini AI Code Reviewer")
st.title("🤖 Gemini AI Code Reviewer")

uploaded_file = st.file_uploader("Upload a ZIP file or single code file", type=["zip", "py", "java", "js", "cpp", "c", "ts", "cs", "rb", "go", "php", "html", "css"])

if uploaded_file:
    if uploaded_file.name.endswith(".zip"):
        project_dir = extract_zip(uploaded_file)
        code_files = get_code_files(project_dir)

        if code_files:
            selected_file = st.selectbox("Select a file to review:", code_files)
            code_content = read_file(selected_file)
            language = selected_file.split('.')[-1]
            st.code(code_content, language=language)

            question = st.text_input("Ask a question about the code:")
            if st.button("Ask Gemini") and question:
                st.spinner("Gemini is thinking...")
                st.write(ask_gemini(question, code_content))

            if st.button("🔧 Refactor Code"):
                st.code(gemini_refactor(code_content), language=language)

            if st.button("🧪 Generate Unit Tests"):
                st.code(gemini_generate_tests(code_content), language='python')

            if st.button("📚 Generate Docstrings"):
                st.code(gemini_generate_docstrings(code_content), language=language)

            if st.button("🔐 Run Security Audit"):
                st.write(gemini_security_audit(code_content))

            if st.button("📄 Generate Code Summary"):
                st.write(gemini_generate_summary(code_content))

            error_msg = st.text_area("Paste an error message (optional):")
            if st.button("❓ Explain Error") and error_msg.strip():
                st.write(gemini_explain_error(code_content, error_msg))

            target_lang = st.selectbox("Translate code to: (Phase 3)", ["", "Java", "Python", "JavaScript", "C++"])
            if st.button("🌐 Translate Code") and target_lang:
                st.code(gemini_translate_code(code_content, target_lang), language=target_lang.lower())

            if st.button("🚀 Optimize Code"):
                st.code(gemini_optimize_code(code_content), language=language)

            if st.button("🎯 Detect Skill Level"):
                st.write(gemini_detect_skill_level(code_content))

            if st.button("📘 Learning Suggestions"):
                st.write(gemini_suggest_learning(code_content))

            if st.button("🐞 Detect Code Smells"):
                st.write(gemini_detect_code_smells(code_content))

        else:
            st.warning("No code files found in the ZIP.")

    else:
        suffix = uploaded_file.name.split('.')[-1]
        code_content = uploaded_file.read().decode('utf-8', errors='ignore')
        st.code(code_content, language=suffix)

        question = st.text_input("Ask a question about the code:")
        if st.button("Ask Gemini") and question:
            st.spinner("Gemini is thinking...")
            st.write(ask_gemini(question, code_content))

        if st.button("🔧 Refactor Code"):
            st.code(gemini_refactor(code_content), language=suffix)

        if st.button("🧪 Generate Unit Tests"):
            st.code(gemini_generate_tests(code_content), language='python')

        if st.button("📚 Generate Docstrings"):
            st.code(gemini_generate_docstrings(code_content), language=suffix)

        if st.button("🔐 Run Security Audit"):
            st.write(gemini_security_audit(code_content))

        if st.button("📄 Generate Code Summary"):
            st.write(gemini_generate_summary(code_content))

        error_msg = st.text_area("Paste an error message (optional):")
        if st.button("❓ Explain Error") and error_msg.strip():
            st.write(gemini_explain_error(code_content, error_msg))

        target_lang = st.selectbox("Translate code to: (Phase 3)", ["", "Java", "Python", "JavaScript", "C++"])
        if st.button("🌐 Translate Code") and target_lang:
            st.code(gemini_translate_code(code_content, target_lang), language=target_lang.lower())

        if st.button("🚀 Optimize Code"):
            st.code(gemini_optimize_code(code_content), language=suffix)

        if st.button("🎯 Detect Skill Level"):
            st.write(gemini_detect_skill_level(code_content))

        if st.button("📘 Learning Suggestions"):
            st.write(gemini_suggest_learning(code_content))

        if st.button("🐞 Detect Code Smells"):
            st.write(gemini_detect_code_smells(code_content))
