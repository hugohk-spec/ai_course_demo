import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(
    page_title="Student Card Generator", 
    page_icon="🎓", 
    layout="centered"
)

st.title("🎓 Student Card Generator")
st.markdown("---")

camera_photo = st.camera_input("Take Photo (Optional)")

with st.form("student_card_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        student_name = st.text_input("Student Name *", placeholder="e.g. John Smith")
        school_name = st.text_input("School Name *", placeholder="e.g. High School")
    
    with col2:
        student_number = st.text_input("Student Number *", placeholder="e.g. 2024001")
        class_form = st.text_input("Class *", placeholder="e.g. 3A")
    
    submitted = st.form_submit_button("Generate Student Card", type="primary", use_container_width=True)

if submitted:
    if not all([student_name, student_number, school_name, class_form]):
        st.error("Please fill in all required fields (marked with *)")
    else:
        # Create student card
        card_width, card_height = 450, 280
        card = Image.new('RGB', (card_width, card_height), color='white')
        draw = ImageDraw.Draw(card)
        
        # Use default fonts (simpler)
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        
        # Draw header
        header_color = '#2563eb'
        draw.rectangle([(0, 0), (card_width, 70)], fill=header_color)
        draw.text((20, 25), "STUDENT CARD", fill='white', font=title_font)
        draw.text((20, 50), school_name, fill='white', font=small_font)
        
        # Draw photo
        photo_size = 90
        photo_x, photo_y = 20, 90
        if camera_photo:
            try:
                photo = Image.open(camera_photo)
                width, height = photo.size
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                photo = photo.crop((left, top, left + size, top + size))
                photo = photo.resize((photo_size, photo_size))
                card.paste(photo, (photo_x, photo_y))
            except:
                draw.rectangle([(photo_x, photo_y), (photo_x + photo_size, photo_y + photo_size)], 
                             outline='#999', width=2)
                draw.text((photo_x + 25, photo_y + 35), "Photo", fill='#999', font=small_font)
        else:
            draw.rectangle([(photo_x, photo_y), (photo_x + photo_size, photo_y + photo_size)], 
                         outline='#999', width=2)
            draw.text((photo_x + 25, photo_y + 35), "Photo", fill='#999', font=small_font)
        
        # Draw student information
        info_x = 130
        y_offset = 95
        
        draw.text((info_x, y_offset), f"Name: {student_name}", fill='black', font=text_font)
        draw.text((info_x, y_offset + 30), f"Student No.: {student_number}", fill='black', font=text_font)
        draw.text((info_x, y_offset + 60), f"Class: {class_form}", fill='black', font=text_font)
        
        # Draw school name at bottom
        draw.text((20, 250), f"School: {school_name}", fill='#666', font=small_font)
        
        # Draw border
        draw.rectangle([(0, 0), (card_width-1, card_height-1)], outline='black', width=2)
        
        # Convert to bytes for display
        img_buffer = io.BytesIO()
        card.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Display the card
        st.success("Student card generated successfully!")
        
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            st.image(img_buffer, caption="Generated Student Card", use_container_width=False)
        
        # Download button
        st.download_button(
            label="Download Student Card",
            data=img_buffer,
            file_name=f"{student_number}_student_card.png",
            mime="image/png",
            use_container_width=True
        )
