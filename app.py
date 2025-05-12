# app.py

import streamlit as st
from graph import build_graph

# Initialize the graph
graph = build_graph()

# Function to run the game
def start_game(state: GameState) -> GameState:
    state["correct_number"] = "5"  # fixed for simplicity
    state["message"] = "Guess a number between 1 and 10:"
    state["end"] = False  # Ensure the game starts without an end condition
    return state

def check_guess(state: GameState) -> GameState:
    if state["guess"] == state["correct_number"]:
        state["message"] = "🎉 Correct! You win!"
        state["end"] = True
    else:
        state["message"] = f"❌ Incorrect. Try again!"
        state["end"] = False
    return state

def build_graph():
    builder = StateGraph(GameState)

    builder.add_node("start", start_game)
    builder.add_node("check", check_guess)

    builder.set_entry_point("start")

    # Connect nodes
    builder.add_edge("start", "check")  # Start to check guess
    builder.add_edge("check", "check", condition=lambda s: not s["end"])  # Keep checking if not ended
    builder.add_edge("check", END, condition=lambda s: s["end"])  # End if the guess is correct

    return builder.compile()

# Run the game
def run_game():
    # Initialize the state
    state = {
        "guess": None,
        "correct_number": "5",  # This can be randomized or modified as needed
        "message": "Guess a number between 1 and 10:",
        "end": False
    }
    
    # Run the graph
    while not state["end"]:
        # Display current message
        st.write(state["message"])
        
        # Input for the guess with a unique key using a dynamic approach
        guess = st.text_input("Enter your guess:", key=f"guess_input_{state['message']}")  # Unique key
        
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
                    "end": False
                }

# Run the game
if __name__ == "__main__":
    st.title("🎮 Gen AI Game App")
    st.header("Number Guessing Game (LangGraph Powered)")
    run_game()
