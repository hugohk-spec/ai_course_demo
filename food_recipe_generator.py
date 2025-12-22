import os
import streamlit as st
import openai
from dotenv import load_dotenv
import re
import requests

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.poe.com/v1",
)

st.set_page_config(page_title="食譜探索器", page_icon="🍳", layout="wide")

st.title("食譜探索器")
st.caption("所有問題都係可選嘅 - 發揮你嘅創意！")

with st.form("recipe_form"):
    question1 = st.selectbox(
        "你而家嘅心情係點？",
        ["", "開心有活力", "舒適放鬆", "大膽冒險", "懷舊溫暖", "清新輕盈", "安慰舒緩", "有趣好玩", "浪漫優雅"],
        help="你而家感覺點？"
    )
    
    question2 = st.selectbox(
        "選擇一個啟發你嘅顏色",
        ["", "紅色", "橙色", "黃色", "綠色", "藍色", "紫色", "粉紅色", "白色", "黑色", "金色"],
        help="今日邊隻顏色吸引你？"
    )
    
    question3 = st.selectbox(
        "邊個時段最適合？",
        ["", "清晨日出", "明亮中午", "黃金下午", "舒適晚上", "深夜"],
        help="你想幾時享用呢餐？"
    )
    
    question4 = st.text_input(
        "現有食材",
        placeholder="例如：雞肉、番茄、意粉、新鮮香草...",
        help="你廚房有咩食材？"
    )
    
    question5 = st.text_area(
        "記憶、情感或故事",
        placeholder="例如：令我想起暑假、令我感覺返到細個、可以將人聚埋一齊...",
        help="呢道菜應該喚起咩感覺或記憶？"
    )
    
    question6 = st.text_input(
        "菜系或地區（可選）",
        placeholder="例如：意大利、日本、地中海...",
        help="有冇特定菜系風格？"
    )
    
    generate_button = st.form_submit_button("✨ 創造我嘅食譜", use_container_width=True, type="primary")

if generate_button:
    prompt_parts = []
    
    if question1:
        prompt_parts.append(f"心情：{question1}")
    
    if question2:
        prompt_parts.append(f"啟發顏色：{question2}")
    
    if question3:
        prompt_parts.append(f"時段：{question3}")
    
    if question4 and question4.strip():
        prompt_parts.append(f"現有食材：{question4.strip()}")
    
    if question5 and question5.strip():
        prompt_parts.append(f"記憶/情感/故事：{question5.strip()}")
    
    if question6 and question6.strip():
        prompt_parts.append(f"菜系風格：{question6.strip()}")
    
    if prompt_parts:
        user_prompt = f"""根據以下元素創造一個創意食譜：
{chr(10).join(prompt_parts)}

食譜應該反映心情（{question1 if question1 else '任何'}），融入顏色主題（{question2 if question2 else '任何'}），並喚起所描述嘅感覺。要特別同難忘！"""
    else:
        user_prompt = "創造一個創意同啟發性嘅食譜，令人驚喜同開心！"
    
    system_prompt = """你係一個創意廚藝藝術家，創造嘅食譜唔只係食物，更係體驗。 
創造食譜時要考慮：
- 心情如何影響菜式嘅特色同呈現
- 如何透過食材同裝飾融入顏色主題
- 時段如何影響菜式風格同上菜方式
- 如何透過味道同呈現喚起所描述嘅記憶或情感

**重要：食譜要簡短精煉，避免冗長描述。**

必須包括：
1. 創意、引人入勝嘅食譜標題
2. 簡短介紹（一兩句，連接心情/顏色/情感）
3. 食材清單（含份量，盡量用符合顏色主題嘅食材）
4. 清晰嘅步驟說明（簡潔，每步一兩句）
5. 烹飪貼士或創意變化（簡短）
6. 準備時間、烹調時間、總時間
7. 上菜建議（簡短）

用繁體中文（粵語）寫，要簡潔、有創意、溫暖。食譜要簡短，重點突出，避免冗長描述。"""
    
    with st.spinner("生成緊食譜..."):
        try:
            response = client.chat.completions.create(
                model="gemini-2.5-pro",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False
            )
            
            recipe = response.choices[0].message.content
            
            # Extract recipe title (first line or first heading)
            recipe_title = "美味食譜"
            lines = recipe.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if line and not line.startswith('#') and len(line) < 100:
                    # Remove markdown formatting
                    recipe_title = re.sub(r'^#+\s*', '', line)
                    recipe_title = re.sub(r'\*\*', '', recipe_title)
                    recipe_title = recipe_title.strip()
                    if recipe_title:
                        break
            
            # Generate image prompt using AI
            image_prompt_text = f"""為呢個食譜創造一個詳細嘅圖片生成提示：{recipe_title}
            
            考慮：
            - 心情：{question1 if question1 else '任何'}
            - 顏色主題：{question2 if question2 else '任何'}
            - 時段：{question3 if question3 else '任何'}
            - 食譜描述：{recipe[:200]}...
            
            只返回一個簡潔、詳細嘅圖片提示（唔好解釋），適合用嚟創造一張吸引、專業嘅食物照片。用繁體中文寫圖片提示。"""
            
            image_url = None
            
            try:
                # Generate optimized image prompt
                image_prompt_response = client.chat.completions.create(
                    model="gemini-2.5-pro",
                    messages=[
                        {"role": "user", "content": image_prompt_text}
                    ],
                    stream=False
                )
                image_prompt = image_prompt_response.choices[0].message.content.strip()
                
                # Generate image using Qwen-Image (following basic_openai.py pattern)
                with st.spinner("用 Qwen-Image 生成緊圖片..."):
                    try:
                        # Use chat completions with Qwen-Image model (as shown in basic_openai.py)
                        qwen_response = client.chat.completions.create(
                            model="Qwen-Image",
                            messages=[
                                {"role": "user", "content": image_prompt}
                            ],
                            extra_body={
                                "aspect": "3:2",    # Options: "1:1", "3:2", "2:3", "auto"
                                "quality": "high"   # Options: "low", "medium", "high"
                            },
                            stream=False
                        )
                        # Get image URL from response content (as shown in basic_openai.py)
                        image_url = qwen_response.choices[0].message.content
                        
                        # Extract URL if it's embedded in text
                        url_match = re.search(r'https?://[^\s\)]+', image_url)
                        if url_match:
                            image_url = url_match.group(0)
                            
                    except Exception as qwen_error:
                        # Fallback: try with simple prompt
                        try:
                            color_name = {"紅色": "red", "橙色": "orange", "黃色": "yellow", "綠色": "green", "藍色": "blue", "紫色": "purple", "粉紅色": "pink", "白色": "white", "黑色": "black", "金色": "gold"}.get(question2, "")
                            simple_prompt = f"A beautiful, professional food photograph of {recipe_title}"
                            if color_name:
                                simple_prompt += f" with {color_name} color accents"
                            simple_prompt += ", appetizing, well-lit, high quality"
                            
                            qwen_response = client.chat.completions.create(
                                model="Qwen-Image",
                                messages=[
                                    {"role": "user", "content": simple_prompt}
                                ],
                                extra_body={
                                    "aspect": "3:2",
                                    "quality": "high"
                                },
                                stream=False
                            )
                            image_url = qwen_response.choices[0].message.content
                            url_match = re.search(r'https?://[^\s\)]+', image_url)
                            if url_match:
                                image_url = url_match.group(0)
                        except Exception as e:
                            raise Exception(f"Qwen-Image generation failed: {str(e)}")
                            
            except Exception as img_error:
                error_msg = str(img_error)
                st.info(f"💡 圖片生成不可用：{error_msg[:150]}。食譜已成功生成！")
            
            st.balloons()
            st.success("食譜已生成！")
            st.divider()
            
            # Display image if generated
            if image_url:
                st.image(image_url, caption=recipe_title, use_container_width=True)
                st.divider()
            
            st.markdown(recipe)
            
            st.session_state.last_recipe = recipe
            st.session_state.last_image_url = image_url
            st.session_state.recipe_preferences = {
                "question1": question1,
                "question2": question2,
                "question3": question3,
                "question4": question4,
                "question5": question5,
                "question6": question6
            }
            
        except Exception as e:
            st.error(f"生成食譜時出錯：{str(e)}")
            st.info("請檢查你嘅 API 金鑰同連線，然後再試一次。")

if "last_recipe" in st.session_state:
    with st.expander("查看上次生成嘅食譜"):
        if "last_image_url" in st.session_state and st.session_state.last_image_url:
            st.image(st.session_state.last_image_url, use_container_width=True)
        st.markdown(st.session_state.last_recipe)

