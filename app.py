
import streamlit as st
import google.generativeai as genai
import zipfile, os, tempfile

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="🔍 Gemini Code Reviewer", layout="wide")
st.title("📂 Gemini Code Reviewer")
st.markdown("Upload a `.zip` of your code project and ask Gemini questions about any file.")

zip_file = st.file_uploader("📦 Upload a ZIP file of your project", type=["zip"])

if "project_chat_history" not in st.session_state:
    st.session_state.project_chat_history = {}

if zip_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        code_files = []
        for root, _, files in os.walk(tmpdir):
            for file in files:
                if file.endswith(('.py', '.java', '.cpp', '.js', '.go', '.cs', '.sql', '.txt')):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, tmpdir)
                    code_files.append((relative_path, full_path))

        selected_file = st.selectbox("📑 Select a file to review", [f[0] for f in code_files])

        full_path = [f[1] for f in code_files if f[0] == selected_file][0]
        with open(full_path, 'r') as f:
            file_content = f.read()

        st.code(file_content, language=selected_file.split('.')[-1])

        st.markdown("### ❓ Ask a question about this file")
        question = st.text_input("Your question")

        if st.button("Ask Gemini"):
            prompt = f"""
You're an expert programmer.
Here is the code from file `{selected_file}`:

```
{file_content}
```

Answer this question about the code:
{question}
"""
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            answer = response.text.strip()

            if selected_file not in st.session_state.project_chat_history:
                st.session_state.project_chat_history[selected_file] = []
            st.session_state.project_chat_history[selected_file].append({"q": question, "a": answer})

        if selected_file in st.session_state.project_chat_history:
            st.markdown("### 💬 Chat History")
            for chat in reversed(st.session_state.project_chat_history[selected_file]):
                st.markdown(f"**You:** {chat['q']}")
                st.markdown(f"**Gemini:** {chat['a']}")
else:
    st.info("Upload a ZIP file to start reviewing a code project.")
