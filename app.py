import sys
import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import time

# Optionally increase recursion limit
sys.setrecursionlimit(1000)

# Define game state structure
class GameState(TypedDict):
    guess: Optional[str]
    correct_number: str
    message: Optional[str]
    end: bool
    guess_count: int  # Counter for guess

# Game state functions
def start_game(state: GameState) -> GameState:
    state["correct_number"] = "5"  # This can be randomized or modified as needed
    state["message"] = "Guess a number between 1 and 10:"
    state["end"] = False
    state["guess_count"] = 0  # Initialize the guess counter
    return state

def check_guess(state: GameState) -> GameState:
    if state["guess"] == state["correct_number"]:
        state["message"] = "🎉 Correct! You win!"
        state["end"] = True  # Set end to True when correct
    else:
        state["message"] = "❌ Incorrect. Try again!"
        state["end"] = False
    state["guess_count"] += 1  # Increment the guess counter
    return state

# Build graph for the game
def build_graph():
    builder = StateGraph(GameState)
    
    builder.add_node("start", start_game)
    builder.add_node("check", check_guess)
    
    builder.set_entry_point("start")
    
    # Add edges without conditions
    builder.add_edge("start", "check")  # Transition from start to check
    builder.add_edge("check", "check")  # Loop from check to check (for retrying)
    builder.add_edge("check", END)  # End the game if guessed correctly
    
    return builder.compile()

graph = build_graph()

# Function to run the game
def run_game():
    # Initialize the state (as a dictionary)
    state = {
        "guess": None,
        "correct_number": "5",
        "message": "Guess a number between 1 and 10:",
        "end": False,
        "guess_count": 0
    }
    
    # Run the graph
    while not state["end"]:
        # Display current message
        st.write(state["message"])
        
        # Generate a unique key based on guess_count and guess (unique for each attempt)
        input_key = f"guess_input_{state['guess_count']}_{state['guess']}_{time.time()}"
        
        # Input for the guess
        guess = st.text_input(f"Enter your guess ({state['message']})", key=input_key)
        
        if guess:
            state["guess"] = guess  # Set the guess
            # Transition to the next state
            state = graph.invoke(state)
        
        # Add a button to restart the game
        if state["end"]:
            if st.button("Restart"):
                state = {
                    "guess": None,
                    "correct_number": "5",  # Reset the correct number
                    "message": "Guess a number between 1 and 10:",
                    "end": False,
                    "guess_count": 0  # Reset the guess count
                }

# Run the game
if __name__ == "__main__":
    st.title("🎮 Gen AI Game App")
    st.header("Number Guessing Game (LangGraph Powered)")
    run_game()
