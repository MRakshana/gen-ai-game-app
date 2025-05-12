import random
import time
import streamlit as st
from typing import Annotated, List, Literal, TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import AnyMessage

# Define your state
class GameState(TypedDict):
    game_type: Literal["number", "word"]
    step: str
    messages: Annotated[List[AnyMessage], "merge"]

# Set up min/max range tracking in session state
if "min_guess" not in st.session_state:
    st.session_state["min_guess"] = 1
if "max_guess" not in st.session_state:
    st.session_state["max_guess"] = 50
if "current_guess" not in st.session_state:
    st.session_state["current_guess"] = None

# Number guessing logic
def number_game_agent(state: GameState) -> GameState:
    messages = state["messages"]

    # Get last guess or make new one
    if st.session_state["current_guess"] is None:
        guess = random.randint(st.session_state["min_guess"], st.session_state["max_guess"])
        st.session_state["current_guess"] = guess
        st.write(f"Is your number {guess}?")
        return state

    guess = st.session_state["current_guess"]

    # Ask for user feedback
    response = st.radio(
        "Select if the guess is correct",
        ["greater", "less", "correct"],
        key=f"radio_{guess}_{len(messages)}"
    )

    if st.button("Submit response", key=f"submit_{guess}_{len(messages)}"):
        if response == "correct":
            st.success(f"🎉 Yay! I guessed your number: {guess}")
            st.session_state["game_counter"] += 1
            st.session_state["state"] = "main"
            st.session_state["current_guess"] = None
            st.session_state["min_guess"] = 1
            st.session_state["max_guess"] = 50
            return {"game_type": "number", "step": "done", "messages": []}
        elif response == "greater":
            st.session_state["min_guess"] = min(50, guess + 1)
        elif response == "less":
            st.session_state["max_guess"] = max(1, guess - 1)

        # Make next guess
        if st.session_state["min_guess"] > st.session_state["max_guess"]:
            st.error("Inconsistent responses. No numbers left to guess.")
            st.session_state["state"] = "main"
            return {"game_type": "number", "step": "error", "messages": []}

        new_guess = (st.session_state["min_guess"] + st.session_state["max_guess"]) // 2
        st.session_state["current_guess"] = new_guess
        st.rerun()

    return state

# Word clue logic (unchanged)
def word_game_agent(state: GameState) -> GameState:
    words = ["apple", "chair", "elephant", "guitar", "rocket", "pencil", "pizza", "tiger"]
    if "word_choice" not in st.session_state:
        st.session_state["word_choice"] = random.choice(words)
        st.session_state["word_guesses"] = []

    st.write("Choose a word from the following list:")
    st.json({i: w for i, w in enumerate(words)})

    question = st.text_input("Ask a yes/no question to guess the word:")
    if question:
        answer = "Maybe"
        target_word = st.session_state["word_choice"]
        if any(word in target_word for word in question.lower().split()):
            answer = "Yes"
        elif random.random() > 0.5:
            answer = "No"
        st.session_state["word_guesses"].append((question, answer))
        for q, a in st.session_state["word_guesses"]:
            st.radio(q, ["Yes", "No", "Maybe"], index=["Yes", "No", "Maybe"].index(a), key=q)

    return {
        "game_type": "word",
        "step": "word_game",
        "messages": [{"type": "user", "content": question}] if question else []
    }

# Build graph (optional LangGraph logic)
def build_game_graph():
    builder = StateGraph(GameState)
    builder.add_node("number_game", number_game_agent)
    builder.add_node("word_game", word_game_agent)
    builder.set_entry_point("number_game")
    builder.set_finish_point("word_game")
    return builder.compile()

# Streamlit UI
st.title("🎮 Welcome to the Game Hub")

if "game_counter" not in st.session_state:
    st.session_state["game_counter"] = 0
if "state" not in st.session_state:
    st.session_state["state"] = "main"
if "messages" not in st.session_state:
    st.session_state["messages"] = []

game_type = st.radio("Choose a game mode", ["Number Game", "Word Clue Guesser"])

if st.button(f"Start {game_type}"):
    st.session_state["state"] = "number" if "Number" in game_type else "word"
    st.session_state["messages"] = []
    st.session_state["current_guess"] = None
    st.session_state["min_guess"] = 1
    st.session_state["max_guess"] = 50

if st.session_state["state"] == "number":
    st.write("Welcome to the Number Game!")
    st.write("Think of a number between 1 and 50, and I'll guess it.")
    state = {
        "game_type": "number",
        "step": "number_game",
        "messages": st.session_state.get("messages", [])
    }
    number_game_agent(state)

elif st.session_state["state"] == "word":
    st.write("Welcome to the Word Clue Guesser!")
    word_game_agent({"game_type": "word", "step": "start", "messages": []})

elif st.session_state["state"] == "main":
    st.write(f"Number Game counter: {st.session_state['game_counter']}")
    st.write("Returning to the main menu...")
    time.sleep(2)
    st.session_state["state"] = ""
