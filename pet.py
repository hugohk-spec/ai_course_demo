import streamlit as st
import os
from dotenv import load_dotenv
import openai

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.poe.com/v1",
)

# Sample pet images (using placeholder images)
PET_IMAGES = {
    "Dog": "https://via.placeholder.com/400x300?text=Dog",
    "Cat": "https://via.placeholder.com/400x300?text=Cat",
    "Bird": "https://via.placeholder.com/400x300?text=Bird",
    "Fish": "https://via.placeholder.com/400x300?text=Fish",
    "Rabbit": "https://via.placeholder.com/400x300?text=Rabbit",
    "Hamster": "https://via.placeholder.com/400x300?text=Hamster",
    "Turtle": "https://via.placeholder.com/400x300?text=Turtle",
    "Snake": "https://via.placeholder.com/400x300?text=Snake",
    "Guinea Pig": "https://via.placeholder.com/400x300?text=Guinea+Pig",
    "Ferret": "https://via.placeholder.com/400x300?text=Ferret",
}

def main():
    st.set_page_config(page_title="Pet Matchmaker", page_icon="🐾")
    
    st.title("AI Pet Matchmaker 🐾")
    
    st.write("Describe your personality, lifestyle, and preferences, and our AI will suggest the perfect pets for you!")
    
    personality = st.text_area("Describe yourself:", height=200, placeholder="E.g., I'm energetic, love outdoor activities, have a busy schedule, prefer low-maintenance pets...")
    
    if st.button("Find My Perfect Pets"):
        if personality.strip():
            with st.spinner("Analyzing your personality and finding perfect pet matches..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a pet matching expert. Based on the user's personality description, suggest exactly 3 pet options that would best suit them. Format your response as:\n\nPet 1: [Pet Name] - [2-3 sentence explanation]\n\nPet 2: [Pet Name] - [2-3 sentence explanation]\n\nPet 3: [Pet Name] - [2-3 sentence explanation]\n\nBe specific about the pet type (e.g., Golden Retriever dog, Siamese cat) and explain why it matches their personality."},
                            {"role": "user", "content": f"Based on this personality: {personality}, suggest 3 perfect pets."}
                        ]
                    )
                    
                    ai_response = response.choices[0].message.content
                    
                    # Parse the response
                    pets = []
                    lines = ai_response.split('\n')
                    current_pet = None
                    current_reason = ""
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('Pet 1:') or line.startswith('Pet 2:') or line.startswith('Pet 3:'):
                            if current_pet:
                                pets.append({'name': current_pet, 'reason': current_reason.strip()})
                            parts = line.split(' - ', 1)
                            if len(parts) == 2:
                                current_pet = parts[0].replace('Pet 1:', '').replace('Pet 2:', '').replace('Pet 3:', '').strip()
                                current_reason = parts[1]
                            else:
                                current_pet = line.replace('Pet 1:', '').replace('Pet 2:', '').replace('Pet 3:', '').strip()
                                current_reason = ""
                        elif current_pet and line:
                            current_reason += " " + line
                    
                    if current_pet:
                        pets.append({'name': current_pet, 'reason': current_reason.strip()})
                    
                    if len(pets) < 3:
                        # Fallback: show raw response
                        st.warning("Could not parse pet suggestions properly. Here's the AI response:")
                        st.write(ai_response)
                        return
                    
                    if len(pets) >= 3:
                        st.success("Here are your top 3 pet matches!")
                        
                        for i, pet in enumerate(pets[:3], 1):
                            pet_name = pet.get('name', 'Unknown Pet')
                            reason = pet.get('reason', 'No reason provided')
                            
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                # Show pet image
                                response = client.chat.images.generate(
                                    model="Qwen-Image",
                                    messages=[
                                        {"role": "system", "content": "You are an image generation model."},
                                        {"role": "user", "content": f"Generate a realistic image of a {pet_name}."}
                                ],
                                    extra_body={
                                        "aspect": "4:3",
                                        "quality": "high"
                                    },
                                stream=False)
                                image_url = response.data[0].url
                                print(image_url)
                            
                            with col2:
                                st.subheader(f"#{i}: {pet_name}")
                                st.write(reason)
                                st.markdown("---")
                    else:
                        st.error("Could not get 3 pet suggestions. Please try again.")
                        
                except Exception as e:
                    st.error(f"Error finding pets: {str(e)}")
        else:
            st.warning("Please describe your personality first.")

if __name__ == "__main__":
    main()
