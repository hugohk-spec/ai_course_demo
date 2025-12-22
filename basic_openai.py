"""
================================================================================
BASIC OPENAI CONCEPTS
================================================================================
Topics to cover:
• Simple chat completion
• System prompts
• Conversation memory
• Image generation
================================================================================
"""

import os
import openai
from dotenv import load_dotenv

# Setup
load_dotenv()
API_KEY = os.getenv("API_KEY")
client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.poe.com/v1",
)

# ============================================================================
# 1. SIMPLE CHAT
# ============================================================================
# Simple one-shot chat
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "What is artificial intelligence?"}
    ]
)
print(response.choices[0].message.content)

# Note: This is the basic way to get a single response from the AI. Remember to 
# keep your API key secret by using environment variables!

# ============================================================================
# 2. WITH SYSTEM PROMPT
# ============================================================================
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a friendly teacher who explains concepts simply"},
        {"role": "user", "content": "What is artificial intelligence?"}
    ]
)
print(response.choices[0].message.content)

# Note: Adding a system message helps guide how the AI responds. It's like giving 
# the AI a character or role to play.

# ============================================================================
# 3. STORING CONVERSATIONS
# ============================================================================
conversation = [
    {"role": "system", "content": "You are a friendly teacher who explains concepts simply"},
    {"role": "user", "content": "What is artificial intelligence?"},
    {"role": "assistant", "content": "AI is like teaching computers to think and learn!"},
    {"role": "user", "content": "Can you give me an example?"}
]

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=conversation
)
print(response.choices[0].message.content)

# Note: By keeping track of the conversation history, the AI can understand context 
# and provide more relevant responses.

# ============================================================================
# 4. IMAGE GENERATION
# ============================================================================
# Example: Using aspect ratio and quality with image generation models
response = client.chat.completions.create(
    model="Qwen-Image",
    messages=[{"role": "user", "content": "A robot making pancakes"}],
    extra_body={
        "aspect": "3:2",    # Options: "1:1", "3:2", "2:3", "auto"
        "quality": "high"   # Options: "low", "medium", "high"
    },
    stream=False  # Recommended for image generation
)

# To get the image URL from the response:
image_url = response.choices[0].message.content  # The model usually returns the image URL in its content
print(image_url)

# Note: OpenAI can also create images based on text descriptions. This is useful 
# for creating visual content for your applications.
