import streamlit as st

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = [['' for _ in range(3)] for _ in range(3)]
if 'current_player' not in st.session_state:
    st.session_state.current_player = 'X'
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

def check_winner(board):
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] != '':
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != '':
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != '':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != '':
        return board[0][2]
    
    # Check for draw
    if all(cell != '' for row in board for cell in row):
        return 'Draw'
    
    return None

def make_move(row, col):
    if st.session_state.board[row][col] == '' and not st.session_state.game_over:
        st.session_state.board[row][col] = st.session_state.current_player
        winner = check_winner(st.session_state.board)
        if winner:
            st.session_state.winner = winner
            st.session_state.game_over = True
        else:
            st.session_state.current_player = 'O' if st.session_state.current_player == 'X' else 'X'

def reset_game():
    st.session_state.board = [['' for _ in range(3)] for _ in range(3)]
    st.session_state.current_player = 'X'
    st.session_state.winner = None
    st.session_state.game_over = False

st.title("Tic Tac Toe")

# Display current player or winner
if st.session_state.winner:
    if st.session_state.winner == 'Draw':
        st.header("It's a Draw!")
    else:
        st.header(f"Player {st.session_state.winner} wins!")
elif not st.session_state.game_over:
    st.header(f"Current player: {st.session_state.current_player}")

# Create the board
cols = st.columns(3)
for i in range(3):
    with cols[i]:
        for j in range(3):
            if st.button(st.session_state.board[j][i] if st.session_state.board[j][i] else ' ', key=f"{j}-{i}", disabled=st.session_state.game_over):
                make_move(j, i)
                st.rerun()

# Reset button
if st.button("Reset Game"):
    reset_game()
    st.rerun()