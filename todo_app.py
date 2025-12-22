import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="To-Do List App", 
    page_icon="✅", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .task-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .completed-task {
        opacity: 0.6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✅ To-Do List App")
st.caption("Stay organized and get things done!")
st.markdown("---")

# Initialize session state
if "todos" not in st.session_state:
    st.session_state.todos = []

if "completed" not in st.session_state:
    st.session_state.completed = []

# Sidebar for adding new tasks
with st.sidebar:
    st.header("➕ Add New Task")
    
    new_task = st.text_input(
        "Task Description", 
        placeholder="e.g., Complete math homework...",
        help="Enter what you need to do"
    )
    
    priority = st.selectbox(
        "Priority Level", 
        ["Low 🟢", "Medium 🟡", "High 🔴"],
        help="Set the priority for this task"
    )
    
    # Extract priority level
    priority_level = priority.split()[0]
    
    col1, col2 = st.columns(2)
    with col1:
        add_clicked = st.button("➕ Add", type="primary", use_container_width=True)
    
    with col2:
        clear_all = st.button("🗑️ Clear All", use_container_width=True)
    
    if add_clicked:
        if new_task.strip():
            task_data = {
                "id": len(st.session_state.todos) + len(st.session_state.completed) + 1,
                "task": new_task.strip(),
                "priority": priority_level,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.todos.append(task_data)
            st.success("✅ Task added!")
            st.rerun()
        else:
            st.warning("⚠️ Please enter a task description!")
    
    if clear_all:
        if st.session_state.todos or st.session_state.completed:
            st.session_state.todos = []
            st.session_state.completed = []
            st.success("🗑️ All tasks cleared!")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Total", len(st.session_state.todos) + len(st.session_state.completed))
    st.metric("Pending", len(st.session_state.todos))
    st.metric("Done", len(st.session_state.completed))

# Main content area
col1, col2 = st.columns(2)

# Pending tasks
with col1:
    st.subheader(f"📋 Pending Tasks ({len(st.session_state.todos)})")
    
    if st.session_state.todos:
        for todo in st.session_state.todos:
            # Priority color coding
            priority_info = {
                "High": {"emoji": "🔴", "color": "#dc3545"},
                "Medium": {"emoji": "🟡", "color": "#ffc107"},
                "Low": {"emoji": "🟢", "color": "#28a745"}
            }
            
            p_info = priority_info.get(todo['priority'], {"emoji": "⚪", "color": "#6c757d"})
            
            with st.container():
                st.markdown(f"""
                <div class="task-card">
                    <h4 style="margin: 0;">
                        {p_info['emoji']} {todo['task']}
                    </h4>
                    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.9em;">
                        Priority: <strong style="color: {p_info['color']};">{todo['priority']}</strong> | 
                        Created: {todo['created_at']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button("✓ Complete", key=f"complete_{todo['id']}", use_container_width=True):
                        todo['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.session_state.completed.append(todo)
                        st.session_state.todos.remove(todo)
                        st.rerun()
                with col_b:
                    if st.button("🗑️ Delete", key=f"delete_{todo['id']}", use_container_width=True):
                        st.session_state.todos.remove(todo)
                        st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("🎉 No pending tasks! Great job!")

# Completed tasks
with col2:
    st.subheader(f"✅ Completed Tasks ({len(st.session_state.completed)})")
    
    if st.session_state.completed:
        for todo in reversed(st.session_state.completed[-10:]):  # Show last 10 completed
            st.markdown(f"""
            <div class="task-card completed-task">
                <p style="margin: 0; text-decoration: line-through;">
                    ✓ {todo['task']}
                </p>
                <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.85em;">
                    Completed: {todo.get('completed_at', 'N/A')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No completed tasks yet. Start checking off tasks!")

# Bottom statistics bar
if st.session_state.todos or st.session_state.completed:
    st.markdown("---")
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    total = len(st.session_state.todos) + len(st.session_state.completed)
    completion_rate = (len(st.session_state.completed) / total * 100) if total > 0 else 0
    
    with col_stat1:
        st.metric("📝 Total Tasks", total)
    with col_stat2:
        st.metric("⏳ Pending", len(st.session_state.todos))
    with col_stat3:
        st.metric("✅ Completed", len(st.session_state.completed))
    with col_stat4:
        st.metric("📈 Completion Rate", f"{completion_rate:.1f}%")
