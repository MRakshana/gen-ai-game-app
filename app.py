import sys
import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

sys.setrecursionlimit(1000)

# Game state structure
class GameState(TypedDict):
    guess: Optional[str]
    correct_number: str
    message: Optional[str]
    end: bool
    guess_count: int

# Game logic
def start_game(state: GameState) -> GameState:
    state["correct_number"] = "5"  # Replace with random if desired
    state["message"] = "Guess a number between 1 and 10:"
    state["end"] = False
    state["guess_count"] = 0
    return state

def check_guess(state: GameState) -> GameState:
    if state["guess"] == state["correct_number"]:
        state["message"] = "🎉 Correct! You win!"
        state["end"] = True
    else:
        state["message"] = "❌ Incorrect. Try again!"
        state["end"] = False
    state["guess_count"] += 1
    return state

def build_graph():
    builder = StateGraph(GameState)
    builder.add_node("start", start_game)
    builder.add_node("check", check_guess)
    builder.set_entry_point("start")
    builder.add_edge("start", "check")
    builder.add_edge("check", "check")
    builder.add_edge("check", END)
    return builder.compile()

graph = build_graph()

# Streamlit game runner
def run_game():
    # Initialize session state
    if "game_state" not in st.session_state:
        st.session_state.game_state = {
            "guess": None,
            "correct_number": "5",
            "message": "Guess a number between 1 and 10:",
            "end": False,
            "guess_count": 0
        }

    state = st.session_state.game_state

    st.write(state["message"])

    # Use a stable input key
    input_key = f"guess_input_{state['guess_count']}"

    guess = st.text_input("Your guess:", key=input_key)

    if guess:
        state["guess"] = guess
        new_state = graph.invoke(state)
        st.session_state.game_state = new_state
        st.experimental_rerun()

    if state["end"]:
        st.success(state["message"])
        if st.button("Restart"):
            st.session_state.game_state = start_game({})
            st.experimental_rerun()

# Run the Streamlit app
if __name__ == "__main__":
    st.title("🎮 Gen AI Game App")
    st.header("Number Guessing Game (LangGraph Powered)")
    run_game()
