import streamlit as st
import random
import time
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Mental Maths Quiz", 
    page_icon="🧮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .question-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem;
        border-radius: 1.5rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s;
    }
    .question-box:hover {
        transform: translateY(-2px);
    }
    .question-text {
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    .result-box {
        padding: 2rem;
        border-radius: 1rem;
        margin: 1.5rem 0;
        text-align: center;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .correct-answer {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 3px solid #28a745;
        color: #155724;
        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
    }
    .wrong-answer {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 3px solid #dc3545;
        color: #721c24;
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
    }
    .timer-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .timer-info {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.2s;
    }
    .stats-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .score-time-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; padding: 1rem;">🧮 Mental Maths Quiz</h1>
        <p style="margin: 0; padding-bottom: 1rem; font-size: 1.2rem;">Test your mental arithmetic skills!</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.total_questions = 0
    st.session_state.correct_answers = 0
    st.session_state.wrong_answers = 0
    st.session_state.current_question = None
    st.session_state.current_answer = None
    st.session_state.question_history = []
    st.session_state.quiz_started = False
    st.session_state.start_time = None
    st.session_state.last_result = None
    st.session_state.question_start_time = None
    st.session_state.time_per_question = []
    st.session_state.total_time = 0
    st.session_state.last_refresh_time = None

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Quiz Settings")
    
    difficulty = st.selectbox(
        "Difficulty Level:",
        ["Easy 🟢", "Medium 🟡", "Hard 🔴"],
        help="Choose the difficulty level"
    )
    
    operation_type = st.selectbox(
        "Operation Type:",
        ["All Operations", "Addition ➕", "Subtraction ➖", "Multiplication ✖️", "Division ➗"],
        help="Choose which operations to practice"
    )
    
    st.markdown("---")
    st.header("📊 Statistics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Questions", st.session_state.total_questions)
        st.metric("Correct", st.session_state.correct_answers)
    with col2:
        st.metric("Wrong", st.session_state.wrong_answers)
        if st.session_state.total_questions > 0:
            accuracy = (st.session_state.correct_answers / st.session_state.total_questions) * 100
            st.metric("Accuracy", f"{accuracy:.1f}%")
    
    # Time statistics
    if st.session_state.total_questions > 0 and st.session_state.time_per_question:
        avg_time = sum(st.session_state.time_per_question) / len(st.session_state.time_per_question)
        st.metric("Avg Time/Question", f"{avg_time:.1f}s")
        
        if st.session_state.total_time > 0:
            questions_per_minute = (st.session_state.total_questions / st.session_state.total_time) * 60
            st.metric("Questions/Min", f"{questions_per_minute:.1f}")
    
    # Score/Time ratio
    if st.session_state.total_time > 0 and st.session_state.correct_answers > 0:
        score_per_second = st.session_state.correct_answers / st.session_state.total_time
        st.metric("Score/Time", f"{score_per_second:.2f}/s")
    
    st.markdown("---")
    if st.button("🔄 Reset Quiz", use_container_width=True, type="primary"):
        st.session_state.score = 0
        st.session_state.total_questions = 0
        st.session_state.correct_answers = 0
        st.session_state.wrong_answers = 0
        st.session_state.current_question = None
        st.session_state.current_answer = None
        st.session_state.question_history = []
        st.session_state.quiz_started = False
        st.session_state.start_time = None
        st.session_state.last_result = None
        st.session_state.question_start_time = None
        st.session_state.time_per_question = []
        st.session_state.total_time = 0
        st.session_state.last_refresh_time = None
        st.rerun()

# Function to generate a question
def generate_question(difficulty_level, operation):
    max_number_map = {
        "Easy 🟢": 20,
        "Medium 🟡": 100,
        "Hard 🔴": 1000
    }
    max_num = max_number_map[difficulty_level]
    
    if operation == "All Operations":
        operation = random.choice(["Addition", "Subtraction", "Multiplication", "Division"])
    
    operation_map = {
        "Addition ➕": "Addition",
        "Subtraction ➖": "Subtraction",
        "Multiplication ✖️": "Multiplication",
        "Division ➗": "Division"
    }
    
    op = operation_map.get(operation, operation)
    
    if op == "Addition":
        num1 = random.randint(1, max_num)
        num2 = random.randint(1, max_num)
        answer = num1 + num2
        question = f"{num1} + {num2} = ?"
        symbol = "➕"
        
    elif op == "Subtraction":
        num1 = random.randint(1, max_num)
        num2 = random.randint(1, num1)  # Ensure positive result
        answer = num1 - num2
        question = f"{num1} - {num2} = ?"
        symbol = "➖"
        
    elif op == "Multiplication":
        if difficulty_level == "Easy 🟢":
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
        elif difficulty_level == "Medium 🟡":
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
        else:  # Hard
            num1 = random.randint(1, 50)
            num2 = random.randint(1, 50)
        answer = num1 * num2
        question = f"{num1} × {num2} = ?"
        symbol = "✖️"
        
    else:  # Division
        if difficulty_level == "Easy 🟢":
            num2 = random.randint(2, 10)
            num1 = num2 * random.randint(1, 10)
        elif difficulty_level == "Medium 🟡":
            num2 = random.randint(2, 20)
            num1 = num2 * random.randint(1, 20)
        else:  # Hard
            num2 = random.randint(2, 50)
            num1 = num2 * random.randint(1, 50)
        answer = num1 // num2
        question = f"{num1} ÷ {num2} = ?"
        symbol = "➗"
    
    return {
        "question": question,
        "answer": answer,
        "symbol": symbol,
        "operation": op
    }

# Initialize start time when page first loads
if st.session_state.start_time is None:
    st.session_state.start_time = time.time()
    st.session_state.last_refresh_time = time.time()

# Generate new question if needed
if st.session_state.current_question is None:
    st.session_state.current_question = generate_question(difficulty, operation_type)
    st.session_state.quiz_started = True
    if st.session_state.question_start_time is None:
        st.session_state.question_start_time = time.time()

# Count-up timer - updates every second
question_data = st.session_state.current_question
current_time = time.time()

# Initialize last_refresh_time if not set
if st.session_state.last_refresh_time is None:
    st.session_state.last_refresh_time = current_time

# Calculate elapsed time from start
elapsed_time = current_time - st.session_state.start_time
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)

# Calculate score per minute
score_per_minute = 0
if elapsed_time > 0:
    score_per_minute = (st.session_state.correct_answers / elapsed_time) * 60

# Display count-up timer with score per minute
timer_display = f"{minutes:02d}:{seconds:02d}"
st.markdown(f"""
<div class="timer-box">
    ⏱️ Elapsed Time: {timer_display}
    <div class="timer-info">Score/Minute: {score_per_minute:.2f}</div>
</div>
""", unsafe_allow_html=True)

# Display current question
st.markdown(f"""
<div class="question-box">
    <p class="question-text">{question_data['symbol']} {question_data['question']}</p>
</div>
""", unsafe_allow_html=True)

# Answer input section
st.markdown("---")
st.markdown("### 💭 Enter Your Answer")

col_input1, col_input2, col_input3 = st.columns([1, 3, 1])
with col_input2:
    user_answer = st.number_input(
        "Your Answer:",
        value=None,
        step=1,
        format="%d",
        key="answer_input",
        help="Enter your answer",
        label_visibility="collapsed"
    )

# Submit button
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    submit_clicked = st.button("✅ Submit Answer", type="primary", use_container_width=True)

# Check answer
if submit_clicked and user_answer is not None:
    # Calculate time taken for this question
    if st.session_state.question_start_time:
        time_taken = time.time() - st.session_state.question_start_time
        st.session_state.time_per_question.append(time_taken)
        st.session_state.total_time += time_taken
    
    st.session_state.total_questions += 1
    correct = user_answer == question_data['answer']
    
    if correct:
        st.session_state.correct_answers += 1
        st.session_state.score += 1
        result_class = "correct-answer"
        result_emoji = "✅"
        result_text = "Correct! Well done!"
    else:
        st.session_state.wrong_answers += 1
        result_class = "wrong-answer"
        result_emoji = "❌"
        result_text = f"Wrong! The correct answer is {question_data['answer']}"
    
    # Calculate time taken for display
    time_taken_display = ""
    if st.session_state.question_start_time:
        time_taken = time.time() - st.session_state.question_start_time
        time_taken_display = f" (Time: {time_taken:.1f}s)"
    
    st.session_state.last_result = {
        "correct": correct,
        "user_answer": user_answer,
        "correct_answer": question_data['answer'],
        "question": question_data['question'],
        "time_taken": time_taken_display
    }
    
    # Add to history
    st.session_state.question_history.append({
        "question": question_data['question'],
        "user_answer": user_answer,
        "correct_answer": question_data['answer'],
        "correct": correct,
        "time_taken": time_taken_display
    })
    
    # Generate new question
    st.session_state.current_question = generate_question(difficulty, operation_type)
    st.session_state.question_start_time = time.time()
    st.rerun()

# Display last result
if st.session_state.last_result:
    result = st.session_state.last_result
    result_class = "correct-answer" if result["correct"] else "wrong-answer"
    result_emoji = "✅" if result["correct"] else "❌"
    
    if result.get("timeout"):
        result_text = f"⏱️ Time's up! The correct answer is **{result['correct_answer']}**"
    elif result["correct"]:
        time_info = result.get("time_taken", "")
        result_text = f"Correct! Well done! 🎉{time_info}"
    else:
        time_info = result.get("time_taken", "")
        result_text = f"Wrong! The correct answer is **{result['correct_answer']}**{time_info}"
    
    st.markdown(f"""
    <div class="result-box {result_class}">
        <h3 style="text-align: center; margin: 0;">
            {result_emoji} {result_text}
        </h3>
    </div>
    """, unsafe_allow_html=True)

# Next question button (only show if there's a result)
if st.session_state.last_result:
    col_next1, col_next2, col_next3 = st.columns([1, 1, 1])
    with col_next2:
        if st.button("➡️ Next Question", use_container_width=True, type="primary"):
            st.session_state.last_result = None
            st.rerun()

# Display statistics and history
st.markdown("---")

# Main statistics row
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.markdown("""
    <div class="stats-card">
        <div class="metric-label">🎯 Score</div>
        <div class="metric-value">{}</div>
    </div>
    """.format(st.session_state.score), unsafe_allow_html=True)

with col_stat2:
    st.markdown("""
    <div class="stats-card">
        <div class="metric-label">✅ Correct</div>
        <div class="metric-value">{}</div>
    </div>
    """.format(st.session_state.correct_answers), unsafe_allow_html=True)

with col_stat3:
    st.markdown("""
    <div class="stats-card">
        <div class="metric-label">❌ Wrong</div>
        <div class="metric-value">{}</div>
    </div>
    """.format(st.session_state.wrong_answers), unsafe_allow_html=True)

with col_stat4:
    if st.session_state.total_questions > 0:
        accuracy = (st.session_state.correct_answers / st.session_state.total_questions) * 100
        st.markdown("""
        <div class="stats-card">
            <div class="metric-label">📊 Accuracy</div>
            <div class="metric-value">{:.1f}%</div>
        </div>
        """.format(accuracy), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="stats-card">
            <div class="metric-label">📊 Accuracy</div>
            <div class="metric-value">0%</div>
        </div>
        """, unsafe_allow_html=True)

# Time and performance statistics
if st.session_state.total_questions > 0:
    st.markdown("---")
    col_time1, col_time2, col_time3, col_time4 = st.columns(4)
    
    with col_time1:
        if st.session_state.start_time:
            total_elapsed = time.time() - st.session_state.start_time
            minutes = int(total_elapsed // 60)
            seconds = int(total_elapsed % 60)
            time_display = f"{minutes}m {seconds}s"
        else:
            time_display = "0s"
        st.markdown("""
        <div class="stats-card">
            <div class="metric-label">⏱️ Total Time</div>
            <div class="metric-value" style="font-size: 1.8rem;">{}</div>
        </div>
        """.format(time_display), unsafe_allow_html=True)
    
    with col_time2:
        if st.session_state.time_per_question:
            avg_time = sum(st.session_state.time_per_question) / len(st.session_state.time_per_question)
            st.markdown("""
            <div class="stats-card">
                <div class="metric-label">⚡ Avg Time/Q</div>
                <div class="metric-value" style="font-size: 1.8rem;">{:.1f}s</div>
            </div>
            """.format(avg_time), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="stats-card">
                <div class="metric-label">⚡ Avg Time/Q</div>
                <div class="metric-value" style="font-size: 1.8rem;">-</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_time3:
        if st.session_state.total_time > 0:
            questions_per_minute = (st.session_state.total_questions / st.session_state.total_time) * 60
            st.markdown("""
            <div class="stats-card">
                <div class="metric-label">🚀 Speed</div>
                <div class="metric-value" style="font-size: 1.8rem;">{:.1f}/min</div>
            </div>
            """.format(questions_per_minute), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="stats-card">
                <div class="metric-label">🚀 Speed</div>
                <div class="metric-value" style="font-size: 1.8rem;">-</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_time4:
        if st.session_state.total_time > 0 and st.session_state.correct_answers > 0:
            score_per_second = st.session_state.correct_answers / st.session_state.total_time
            st.markdown("""
            <div class="stats-card">
                <div class="metric-label">💯 Score/Time</div>
                <div class="metric-value" style="font-size: 1.8rem;">{:.2f}/s</div>
            </div>
            """.format(score_per_second), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="stats-card">
                <div class="metric-label">💯 Score/Time</div>
                <div class="metric-value" style="font-size: 1.8rem;">-</div>
            </div>
            """, unsafe_allow_html=True)

# Question history
if st.session_state.question_history:
    st.markdown("---")
    st.subheader("📜 Recent Questions")
    
    # Show last 10 questions in a nicer format
    recent_history = list(reversed(st.session_state.question_history[-10:]))
    for i, q in enumerate(recent_history, 1):
        status = "✅" if q["correct"] else "❌"
        timeout_marker = " ⏱️" if q.get("timeout") else ""
        time_info = q.get("time_taken", "")
        user_ans = q['user_answer'] if q['user_answer'] is not None else "Timeout"
        
        st.markdown(f"""
        <div style="padding: 0.8rem; margin: 0.5rem 0; background: {'#d4edda' if q['correct'] else '#f8d7da'}; 
                    border-radius: 0.5rem; border-left: 4px solid {'#28a745' if q['correct'] else '#dc3545'};">
            <strong>{i}.</strong> {status}{timeout_marker} <strong>{q['question']}</strong><br>
            Your answer: <strong>{user_ans}</strong> | Correct: <strong>{q['correct_answer']}</strong>{time_info}
        </div>
        """, unsafe_allow_html=True)

# Instructions
if not st.session_state.quiz_started:
    st.info("👆 Configure your quiz settings in the sidebar and start answering questions!")

# Auto-refresh timer every second (at the end to avoid interrupting user interactions)
current_time_end = time.time()
if st.session_state.last_refresh_time is None:
    st.session_state.last_refresh_time = current_time_end

time_since_last_refresh = current_time_end - st.session_state.last_refresh_time
if time_since_last_refresh >= 1.0:
    st.session_state.last_refresh_time = current_time_end
    st.rerun()
