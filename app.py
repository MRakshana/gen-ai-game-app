import streamlit as st
from typing import TypedDict
from langgraph.graph import StateGraph, END
import random

# 1. Define the state schema
class GameState(TypedDict):
    _next: list[str]  # List of nodes to transition to
    value: int
    word_to_guess: str
    guessed_word: str

# 2. Define your node functions with added debug prints
def start_node(state: GameState) -> GameState:
    st.write("\n[Start Node]")
    value = state["value"]
    next_steps = []

    # Number guessing game logic
    if value % 2 == 0:
        next_steps.append("check_even")
    else:
        next_steps.append("check_odd")

    if value > 0:
        next_steps.append("check_positive")
    else:
        next_steps.append("check_non_positive")

    st.write(f"Next steps (Number Game): {next_steps}")
    return {"_next": next_steps, "value": value, "word_to_guess": state["word_to_guess"], "guessed_word": state["guessed_word"]}

def check_even(state: GameState) -> GameState:
    st.write(f"✔️ It's even! Current value: {state['value']}")
    return {"_next": [END], "value": state["value"], "word_to_guess": state["word_to_guess"], "guessed_word": state["guessed_word"]}

def check_odd(state: GameState) -> GameState:
    st.write(f"✔️ It's odd! Current value: {state['value']}")
    return {"_next": [END], "value": state["value"], "word_to_guess": state["word_to_guess"], "guessed_word": state["guessed_word"]}

def check_positive(state: GameState) -> GameState:
    st.write(f"✔️ It's positive! Current value: {state['value']}")
    return {"_next": [END], "value": state["value"], "word_to_guess": state["word_to_guess"], "guessed_word": state["guessed_word"]}

def check_non_positive(state: GameState) -> GameState:
    st.write(f"✔️ It's zero or negative! Current value: {state['value']}")
    return {"_next": [END], "value": state["value"], "word_to_guess": state["word_to_guess"], "guessed_word": state["guessed_word"]}

# 3. Word Guessing Game Logic
def start_word_game(state: GameState) -> GameState:
    word_list = ['apple', 'banana', 'cherry', 'date', 'elderberry']
    word_to_guess = random.choice(word_list)  # Pick a random word from the list
    st.write(f"Welcome to the Word Guessing Game! Try to guess the word.")
    st.write(f"Word to guess: {word_to_guess}")  # Normally, this would be hidden
    return {"_next": ["check_word_guess"], "value": state["value"], "word_to_guess": word_to_guess, "guessed_word": ""}

def check_word_guess(state: GameState) -> GameState:
    guessed_word = state["guessed_word"]
    word_to_guess = state["word_to_guess"]

    if guessed_word.lower() == word_to_guess.lower():
        st.write(f"✔️ Correct! You've guessed the word: {guessed_word}")
        return {"_next": [END], "value": state["value"], "word_to_guess": word_to_guess, "guessed_word": guessed_word}
    else:
        st.write(f"❌ Incorrect! Try again.")
        return {"_next": ["check_word_guess"], "value": state["value"], "word_to_guess": word_to_guess, "guessed_word": ""}

# 4. Create the graph
builder = StateGraph(GameState)

# Add nodes to the graph
builder.add_node("start", start_node)
builder.add_node("check_even", check_even)
builder.add_node("check_odd", check_odd)
builder.add_node("check_positive", check_positive)
builder.add_node("check_non_positive", check_non_positive)
builder.add_node("start_word_game", start_word_game)
builder.add_node("check_word_guess", check_word_guess)

# Set the entry point
builder.set_entry_point("start")

# Define edges to terminate the graph
builder.add_edge("check_even", END)
builder.add_edge("check_odd", END)
builder.add_edge("check_positive", END)
builder.add_edge("check_non_positive", END)
builder.add_edge("check_word_guess", END)

# Compile the graph
graph = builder.compile()

# 5. Streamlit UI
st.title("LangGraph Game - Number and Word Guesser")
st.write("This is a simple game where you can guess a number (even/odd/positive) and a word!")

# Select the game mode (Number or Word Guessing)
game_mode = st.radio("Choose a game mode", ["Number Guessing", "Word Guessing"])

# Number Guessing Game Inputs
if game_mode == "Number Guessing":
    number = st.number_input("Enter a number", value=3)
    initial_state = {"_next": ["start"], "value": number, "word_to_guess": "", "guessed_word": ""}

# Word Guessing Game Inputs
elif game_mode == "Word Guessing":
    guessed_word = st.text_input("Enter your guess for the word:")
    initial_state = {"_next": ["start_word_game"], "value": 0, "word_to_guess": "", "guessed_word": guessed_word}

# Button to invoke the game
if st.button("Run Game"):
    st.write("Running LangGraph...")
    graph.invoke(initial_state)
