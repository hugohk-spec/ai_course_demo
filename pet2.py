import streamlit as st
import os
import re
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Check if API Key exists
if not API_KEY:
    st.error("API_KEY not found. Please check your .env file.")
    st.stop()

client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.poe.com/v1",
)

def extract_url(text):
    """
    Extracts the first URL found in a string (handles Markdown format ![alt](url))
    """
    pattern = r'https?://[^\s\)\?]+(?:(?:\?[^\s\)]+)|(?:\.[a-zA-Z0-9]+))'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def main():
    st.set_page_config(page_title="Pet Matchmaker", page_icon="🐾", layout="wide")
    
    st.title("AI Pet Matchmaker 🐾")
    st.write("Describe your personality and lifestyle to find your perfect pet matches!")
    
    personality = st.text_area(
        "Describe yourself:", 
        height=150, 
        placeholder="E.g., I live in a small apartment, work from home, and love quiet evenings..."
    )
    
    if st.button("Find My Perfect Pets"):
        if not personality.strip():
            st.warning("Please enter some details about yourself first.")
            return

        with st.spinner("Analyzing your lifestyle and finding matches..."):
            try:
                # 1. Get Pet Suggestions
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a pet matching expert. Suggest exactly 3 pet types. Format: 'Pet Name: [Name] | Description: [Description]'. Use 2-3 line per pet."},
                        {"role": "user", "content": f"Personality: {personality}"}
                    ]
                )
                
                ai_text = response.choices[0].message.content
                # Simple parsing based on the format requested in the system prompt
                lines = [line for line in ai_text.split('\n') if line.strip()]
                
                st.success("Here are your top 3 pet matches!")
                
                # Display results in columns
                cols = st.columns(3)
                
                for i, line in enumerate(lines[:3]):
                    # Extract name and description
                    if "|" in line:
                        name_part, desc_part = line.split("|", 1)
                        pet_name = name_part.replace("Pet Name:", "").strip()
                        reason = desc_part.replace("Description:", "").strip()
                    else:
                        pet_name = f"Match {i+1}"
                        reason = line

                    with cols[i]:
                        # 2. Generate Image for each pet
                        try:
                            img_response = client.chat.completions.create(
                                model="GPT-Image-1.5",
                                messages=[{"role": "user", "content": f"A high-quality, professional photo of a {pet_name}"}]
                            )
                            raw_content = img_response.choices[0].message.content
                            image_url = extract_url(raw_content)
                            
                            if image_url:
                                st.image(image_url, use_container_width=True)
                            else:
                                st.info("Image could not be generated.")
                        except Exception as e:
                            st.error(f"Image error: {e}")
                        
                        st.subheader(pet_name)
                        st.write(reason)

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()