"""
================================================================================
BASIC STREAMLIT CONCEPTS
================================================================================
Topics to cover:
• Basic display
• User inputs
• Buttons
• Layout
• Chat interface
================================================================================
"""

import streamlit as st

# ============================================================================
# 1. BASIC DISPLAY
# ============================================================================
st.title("My App")
st.write("Hello World!")
st.markdown("**Bold** text")

# Note: These are the basic building blocks of your web app. Think of them as 
# different ways to show information to your users, like titles, normal text, 
# and fancy formatted text.

# ============================================================================
# 2. USER INPUTS
# ============================================================================
name = st.text_input("Enter your name")
age = st.number_input("Enter your age", min_value=0)
option = st.selectbox("Choose fruit", ["apple", "banana"])

# Note: These commands create different ways for users to input information. 
# It's like creating a form that people can fill out on your website.

if name:
    st.write(f"Hello, {name}!")
if age:
    st.write(f"Your age is {age}")
st.write(f"You chose: {option}")

# ============================================================================
# 3. BUTTONS & ACTIONS
# ============================================================================
if st.button("Click me"):
    st.write("Button was clicked!")

# Note: Buttons let users interact with your app. When someone clicks a button, 
# your app can do something in response.

# ============================================================================
# 4. LAYOUT
# ============================================================================
col1, col2 = st.columns(2)
with col1:
    st.write("Left column")
with col2:
    st.write("Right column")

with st.sidebar:
    st.write("Sidebar content")

# Note: Layout helps organize your app's appearance. Columns split the screen 
# into parts, and sidebars create a menu area on the side.

# ============================================================================
# 5. CHAT INTERFACE
# ============================================================================
# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Add assistant response
    assistant_response = "This is where your AI response would go"
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.write(assistant_response)

# Note: This creates a chat interface similar to messaging apps. The session_state 
# helps remember the conversation even when users input new messages, and 
# chat_message creates those familiar chat bubbles we see in messaging apps.
