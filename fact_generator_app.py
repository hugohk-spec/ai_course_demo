import os
import streamlit as st
import openai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.poe.com/v1",
)

# Page configuration
st.set_page_config(
    page_title="AI Fact Generator",
    page_icon="💡",
    layout="wide"
)

# Custom CSS for card styling
st.markdown("""
    <style>
    .fact-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        color: white;
        border-left: 5px solid #ffd700;
    }
    .fact-card h3 {
        color: #ffd700;
        margin-top: 0;
        font-size: 1.2rem;
    }
    .fact-content {
        font-size: 1.1rem;
        line-height: 1.6;
        margin: 0.5rem 0;
    }
    .fact-timestamp {
        font-size: 0.85rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "facts" not in st.session_state:
    st.session_state.facts = []

# Header
st.title("💡 AI-Powered Random Fact Generator")
st.markdown("Generate interesting random facts and collect them in beautiful cards!")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Category selection
    category = st.selectbox(
        "Choose a category:",
        [
            "Random",
            "Science",
            "History",
            "Nature",
            "Technology",
            "Space",
            "Animals",
            "Geography",
            "Culture",
            "Food"
        ],
        index=0
    )
    
    # Model selection
    model = st.selectbox(
        "Choose AI model:",
        ["gemini-2.5-pro", "gpt-4", "claude-3-opus", "llama-3.1-405b"],
        index=0
    )
    
    # Clear facts button
    st.divider()
    if st.button("🗑️ Clear All Facts", use_container_width=True):
        st.session_state.facts = []
        st.rerun()
    
    # Stats
    st.divider()
    st.metric("Total Facts", len(st.session_state.facts))

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    # Generate fact button
    if st.button("✨ Generate New Fact", use_container_width=True, type="primary"):
        with st.spinner("Generating an interesting fact..."):
            try:
                # Create prompt based on category
                if category == "Random":
                    prompt = "Generate a fascinating, true, and interesting random fact. Make it concise (1-2 sentences) and engaging. Provide the fact in BOTH English and Traditional Chinese. Format your response as:\n\nEnglish: [fact in English]\nTraditional Chinese: [fact in Traditional Chinese]"
                else:
                    prompt = f"Generate a fascinating, true, and interesting fact about {category.lower()}. Make it concise (1-2 sentences) and engaging. Provide the fact in BOTH English and Traditional Chinese. Format your response as:\n\nEnglish: [fact in English]\nTraditional Chinese: [fact in Traditional Chinese]"
                
                # Get AI response
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a knowledgeable fact generator. Provide interesting, accurate, and engaging facts in both English and Traditional Chinese. Keep responses concise and factual. Always format your response with 'English:' and 'Traditional Chinese:' labels."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    stream=False
                )
                
                response_text = response.choices[0].message.content.strip()
                
                # Parse English and Traditional Chinese from response
                fact_text_en = ""
                fact_text_zh_tw = ""
                
                if "English:" in response_text and "Traditional Chinese:" in response_text:
                    parts = response_text.split("Traditional Chinese:")
                    if len(parts) == 2:
                        fact_text_en = parts[0].replace("English:", "").strip()
                        fact_text_zh_tw = parts[1].strip()
                elif "English:" in response_text:
                    fact_text_en = response_text.replace("English:", "").strip()
                elif "Traditional Chinese:" in response_text:
                    fact_text_zh_tw = response_text.replace("Traditional Chinese:", "").strip()
                else:
                    # Fallback: treat entire response as English
                    fact_text_en = response_text
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Add fact to session state
                st.session_state.facts.append({
                    "text_en": fact_text_en,
                    "text_zh_tw": fact_text_zh_tw,
                    "category": category,
                    "timestamp": timestamp
                })
                
                st.success("Fact generated successfully! ✨")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating fact: {str(e)}")

with col2:
    st.write("")  # Spacing

# Display facts in cards
if st.session_state.facts:
    st.divider()
    st.subheader(f"📚 Your Fact Collection ({len(st.session_state.facts)} facts)")
    
    # Display facts in reverse order (newest first)
    for idx, fact in enumerate(reversed(st.session_state.facts)):
        # Handle both old format (text) and new format (text_en, text_zh_tw)
        fact_en = fact.get('text_en', fact.get('text', ''))
        fact_zh_tw = fact.get('text_zh_tw', '')
        
        # Create card using markdown with custom styling
        if fact_zh_tw:
            card_html = f"""
            <div class="fact-card">
                <h3>💡 {fact['category']} Fact #{len(st.session_state.facts) - idx}</h3>
                <div class="fact-content">
                    <strong>🇬🇧 English:</strong><br>{fact_en}<br><br>
                    <strong>🇹🇼 繁體中文:</strong><br>{fact_zh_tw}
                </div>
                <div class="fact-timestamp">🕒 {fact['timestamp']}</div>
            </div>
            """
        else:
            # Fallback for old format facts
            card_html = f"""
            <div class="fact-card">
                <h3>💡 {fact['category']} Fact #{len(st.session_state.facts) - idx}</h3>
                <div class="fact-content">{fact_en}</div>
                <div class="fact-timestamp">🕒 {fact['timestamp']}</div>
            </div>
            """
        st.markdown(card_html, unsafe_allow_html=True)
else:
    st.info("👆 Click the button above to generate your first fact!")

# Footer
st.divider()
st.caption("💡 Powered by AI • Facts are generated using advanced language models")

