import streamlit as st

from agents.coordinator import route_query
from core.config import DEFAULT_DOCS_DIR

st.set_page_config(page_title="CS Student Copilot", layout="wide")

st.title("CS Student Copilot 🤖")
st.write("Your all-in-one assistant for coding, research, and course materials.")

# Agent Selection
st.sidebar.title("Agent Persona")
agent_choice = st.sidebar.radio(
    "Choose your assistant:",
    ("CodeHelper", "ScholarScout", "StudyBuddy")
)

# Session State Management
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_agent" not in st.session_state or st.session_state.current_agent != agent_choice:
    st.session_state.current_agent = agent_choice
    st.session_state.messages = [] # Clear history on agent switch
    st.rerun()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mapping of UI choice to the agent_name the coordinator expects
agent_dispatcher = {
    "CodeHelper": "codehelper",
    "ScholarScout": "scholarscout",
    "StudyBuddy": "studybuddy"
}
selected_agent_id = agent_dispatcher[st.session_state.current_agent]

# StuddyBuddy specific UI section for indexing
if st.session_state.current_agent == "StudyBuddy":
    with st.expander("📚 Manage Knowledge Base"):
        st.write("Index your course materials to make them searchable.")
        
        with st.form("index_form", clear_on_submit=True):
            docs_path = st.text_input("Directory Path", value=str(DEFAULT_DOCS_DIR), help="The folder containing your .txt and .pdf files.")
            force_recreate = st.checkbox("Force Re-creation", help="If checked, deletes the existing knowledge base and builds a new one.")
            submitted = st.form_submit_button("Index Documents")

            if submitted:
                with st.spinner(f"Indexing documents in '{docs_path}'... This may take a moment."):
                    index_query = f"Please index the documents in the directory '{docs_path}'. Force recreate is set to {force_recreate}."
                    response = route_query(query=index_query, agent_name="studybuddy")
                    st.success(response)

# Chat Input
if prompt := st.chat_input(f"Ask {st.session_state.current_agent}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"{st.session_state.current_agent} is thinking..."):
            if selected_agent_id == "studybuddy":
                final_prompt = prompt
            else:
                final_prompt = prompt
            
            response = route_query(query=final_prompt, agent_name=selected_agent_id)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})