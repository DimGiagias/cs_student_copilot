import streamlit as st

from agents.coordinator import route_query
from core.config import DEFAULT_DOCS_DIR

st.set_page_config(
    page_title="CS Student Copilot",
    page_icon="🤖",
    layout="centered"
)

# session state Management
if "current_agent" not in st.session_state:
    st.session_state.current_agent = "CodeHelper"
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("🤖 CS Copilot")
    st.write("Choose your assistant:")

    agents = {
        "CodeHelper": {"icon": "👨‍💻", "id": "codehelper"},
        "ScholarScout": {"icon": "🎓", "id": "scholarscout"},
        "StudyBuddy": {"icon": "📖", "id": "studybuddy"},
    }
    
    for agent_name, props in agents.items():
        if st.button(f"{props['icon']} {agent_name}", use_container_width=True):
            if st.session_state.current_agent != agent_name:
                st.session_state.current_agent = agent_name
                st.session_state.messages = []
                st.rerun()

    st.divider()
    st.subheader("Project Links")
    st.link_button("View on GitHub", "https://github.com/DimGiagias/cs_student_copilot.git", use_container_width=True)
    st.link_button("Read the Docs", "https://github.com/DimGiagias/cs_student_copilot/blob/master/README.md", use_container_width=True)


selected_agent_name = st.session_state.current_agent
selected_agent_props = agents[selected_agent_name]
st.header(f"{selected_agent_props['icon']} Chat with {selected_agent_name}")

# Agent-specific UI for StudyBuddy
if selected_agent_name == "StudyBuddy":
    with st.expander("📚 Manage Knowledge Base"):
        st.write("Index your course materials to make them searchable.")
        with st.form("index_form", clear_on_submit=True):
            docs_path = st.text_input("Directory Path", value=str(DEFAULT_DOCS_DIR), help="The folder containing your .txt and .pdf files.")
            force_recreate = st.checkbox("Force Re-creation", help="If checked, deletes the existing knowledge base.")
            submitted = st.form_submit_button("Index Documents")

            if submitted:
                with st.spinner(f"Indexing documents in '{docs_path}'..."):
                    index_query = f"Please index the documents in '{docs_path}'. Force recreate is set to {force_recreate}."
                    response = route_query(query=index_query, agent_name=selected_agent_props['id'])
                    st.success(response)

# display welcome message and example prompts if chat is empty
if not st.session_state.messages:
    example_prompts = {
        "CodeHelper": [
            "Write a Python function to sort a list of dictionaries by a specific key.",
            "Explain the concept of recursion with a code example.",
        ],
        "ScholarScout": [
            "Find 3 recent papers about large language models.",
            "What is the abstract of the paper with ID '1706.03762'?",
        ],
        "StudyBuddy": [
            # "Summarize my notes on the key concepts of machine learning.",
            # "List the important formulas from my 'calculus_cheatsheet.pdf'.",
        ]
    }
    
    prompts_for_agent = example_prompts[selected_agent_name]

    
    st.markdown("### Welcome! How can I help you today?")
    if prompts_for_agent: st.write("Or try one of these examples to get started:")

    cols = st.columns(2)
    
    if prompts_for_agent:
        for i, col in enumerate(cols):
            with col:
                if st.button(prompts_for_agent[i], use_container_width=True):
                    prompt = prompts_for_agent[i]
                    
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    
                    with st.chat_message("assistant"):
                        with st.spinner(f"{selected_agent_name} is thinking..."):
                            response = route_query(query=prompt, agent_name=selected_agent_props['id'])
                            st.markdown(response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

# display the previous chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# chat input
if prompt := st.chat_input(f"Ask {selected_agent_name}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"{selected_agent_name} is thinking..."):
            response = route_query(query=prompt, agent_name=selected_agent_props['id'])
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})