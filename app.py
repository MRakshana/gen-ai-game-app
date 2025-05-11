import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

# Define GameState TypedDict
class GameState(TypedDict):
    _next: str
    number_guess_min: int
    number_guess_max: int
    number_game_count: int
    word_game_count: int
    session_games: list[str]

# Initialize the state with default values
def initialize_state() -> GameState:
    return {
        "_next": "menu",
        "number_guess_min": 1,
        "number_guess_max": 50,
        "number_game_count": 0,
        "word_game_count": 0,
        "session_games": [],
    }

# Menu agent
def menu(state: GameState) -> GameState:
    st.title("🧠 Gen AI Game App")
    st.subheader("Choose a game")
    col1, col2 = st.columns(2)

    if col1.button("Play Number Guessing Game"):
        state["_next"] = "start_number_game"
    elif col2.button("Play Word Clue Game"):
        state["_next"] = "start_word_game"
    else:
        state["_next"] = "menu"

    return state

# Number guessing game agent
def number_game_agent(state: GameState) -> GameState:
    min_val = state.get("number_guess_min", 1)
    max_val = state.get("number_guess_max", 50)
    mid = (min_val + max_val) // 2

    st.subheader("🔢 Number Guessing Game")
    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)

    user_input = None
    if col1.button("Yes"):
        user_input = "yes"
    elif col2.button("No"):
        user_input = "no"

    # Apply user response if present
    if user_input == "yes":
        state["number_guess_min"] = mid + 1
    elif user_input == "no":
        state["number_guess_max"] = mid

    # Check if number is guessed
    if state["number_guess_min"] >= state["number_guess_max"]:
        st.success(f"🎯 Your number is {state['number_guess_min']}! I guessed it!")
        state["number_game_count"] += 1
        state["session_games"]._]()
