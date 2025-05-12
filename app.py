# app.py

import streamlit as st
from graph import build_graph

# Initialize the graph
graph = build_graph()

# Function to run the game
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
