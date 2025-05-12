# app.py (combined with graph.py)
import streamlit as st
from langgraph.graph import StateGraph, END

# --- LangGraph Game Logic (combined from graph.py) ---

def build_game_graph():
    builder = StateGraph()

    # Define your game nodes
    builder.add_node("start_game", start_game_node)
    builder.add_node("play_turn", play_turn_node)
    builder.add_node("check_end", check_end_node)

    # Define entry and edges
    builder.set_entry_point("start_game")
    builder.add_edge("start_game", "play_turn")
    builder.add_edge("play_turn", "check_end")

    builder.add_conditional_edges(
        "check_end", lambda state: END if state.get("end", False) else "play_turn"
    )

    return builder.compile()

# Game state nodes (from graph.py)
def start_game_node(state):
    state["message"] = "Welcome to the Game! Let's start."
    return state

def play_turn_node(state):
    state["message"] = "Your turn! Guess a number."
    # Implement game logic here
    return state

def check_end_node(state):
    if state.get("user_input") == "42":  # Example win condition
        state["message"] = "You win!"
        state["end"] = True
    else:
        state["message"] = "Keep guessing!"
        state["end"] = False
    return state

# --- Streamlit Frontend (combined from app.py) ---

# Initialize runner and stream
if "runner" not in st.session_state:
    st.session_state.runner = build_game_graph()
    st.session_state.iterator = None
    st.session_state.state = None
    st.session_state.done = False

st.title("🎮 Gen AI Game App")

# Start new game
if st.button("Start Game"):
    st.session_state.iterator = st.session_state.runner.stream({})
    st.session_state.state = next(st.session_state.iterator)
    st.session_state.done = False

# Render current state
if st.session_state.state and not st.session_state.done:
    # Display game output based on state contents
    st.write(st.session_state.state.get("message", "Waiting..."))

    # Get user input
    user_input = st.text_input("Your response:", key="user_input")

    if st.button("Submit"):
        st.session_state.state["user_input"] = user_input
        try:
            st.session_state.state = st.session_state.iterator.send(st.session_state.state)
            if st.session_state.state.get("end", False):
                st.success("✅ Game finished!")
                st.session_state.done = True
        except StopIteration:
            st.success("✅ Game finished!")
            st.session_state.done = True
