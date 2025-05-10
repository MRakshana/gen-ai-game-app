from uuid import uuid4  # For unique session ID
from typing import TypedDict, List, Optional
import streamlit as st

# Define the GameState structure
class GameState(TypedDict):
    number_guess_min: int
    number_guess_max: int
    number_game_count: int
    session_games: List[str]
    _next: Optional[str]
    number_game_rounds: int

# Initialize GameState if not already in session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = GameState(
        number_guess_min=1,
        number_guess_max=50,
        number_game_count=0,
        session_games=[],
        _next=None,
        number_game_rounds=0
    )

# Define the agent function for the number game
def number_game_agent(state: GameState) -> GameState:
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2
    session_id = uuid4()  # Generate unique session ID
    game_count = state["number_game_count"]

    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)

    # Create a unique button key using the session ID and game count
    with col1:
        button_key_yes = f"yes_{session_id}_{game_count}_{min_val}_{max_val}"
        if st.button(f"Yes_{session_id}_{game_count}", key=button_key_yes):
            state["number_guess_min"] = mid + 1
            if state["number_guess_min"] == state["number_guess_max"]:
                st.write(f"Your number is {state['number_guess_min']}! I guessed it!")
                state["number_game_count"] += 1
                state["session_games"].append("number")
                state["number_guess_min"] = 1
                state["number_guess_max"] = 50
                state["_next"] = "menu"
            else:
                state["_next"] = "start_number_game"

    with col2:
        button_key_no = f"no_{session_id}_{game_count}_{min_val}_{max_val}"
        if st.button(f"No_{session_id}_{game_count}", key=button_key_no):
            state["number_guess_max"] = mid
            if state["number_guess_min"] == state["number_guess_max"]:
                st.write(f"Your number is {state['number_guess_min']}! I guessed it!")
                state["number_game_count"] += 1
                state["session_games"].append("number")
                state["number_guess_min"] = 1
                state["number_guess_max"] = 50
                state["_next"] = "menu"
            else:
                state["_next"] = "start_number_game"

    return state

# Execute the game logic
state = st.session_state.game_state
state = number_game_agent(state)
st.session_state.game_state = state
