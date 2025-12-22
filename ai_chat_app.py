import os
import streamlit as st
import openai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.poe.com/v1",
)

# Page configuration
st.set_page_config(page_title="AI Chat App", page_icon="💬", layout="wide")

# Sidebar for preprompt and character settings
with st.sidebar:
    st.header("⚙️ AI Settings")
    
    # Character presets
    st.subheader("Character Presets")
    character_preset = st.selectbox(
        "Choose a character:",
        ["Custom", "Friendly Assistant", "Expert Teacher", "Creative Writer", "Tech Support", "Cheerful Friend"]
    )
    
    # Default system prompts for presets
    preset_prompts = {
        "Custom": "",
        "Friendly Assistant": "You are a friendly and helpful AI assistant. Be warm, approachable, and always ready to help.",
        "Expert Teacher": "You are an expert teacher who explains complex topics in simple, easy-to-understand ways. Use examples and analogies.",
        "Creative Writer": "You are a creative writer with a vivid imagination. Help users brainstorm ideas, write stories, and be creative.",
        "Tech Support": "You are a knowledgeable tech support specialist. Provide clear, step-by-step solutions to technical problems.",
        "Cheerful Friend": "You are a cheerful and optimistic friend. Be encouraging, positive, and make conversations fun and engaging."
    }
    
    # System prompt input
    st.subheader("System Prompt / Preprompt")
    if character_preset == "Custom":
        system_prompt = st.text_area(
            "Enter custom system prompt:",
            height=150,
            placeholder="You are a helpful AI assistant...",
            help="This sets the AI's behavior and personality"
        )
    else:
        system_prompt = st.text_area(
            "System prompt (editable):",
            value=preset_prompts[character_preset],
            height=150,
            help="You can modify the preset prompt"
        )
    
    # Model selection
    st.subheader("Model Selection")
    model = st.selectbox(
        "Choose model:",
        ["gemini-2.5-pro", "gpt-4", "claude-3-opus", "llama-3.1-405b"],
        index=0
    )
    
    # Clear chat button
    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("💬 AI Chat App")
st.caption("Chat with an AI assistant. Customize its personality using the sidebar.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare messages for API call
    api_messages = []
    
    # Add system prompt if provided
    if system_prompt and system_prompt.strip():
        api_messages.append({"role": "system", "content": system_prompt.strip()})
    
    # Add conversation history
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    stream=False
                )
                ai_response = response.choices[0].message.content
                st.markdown(ai_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                error_message = f"Error: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

