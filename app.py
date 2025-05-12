import streamlit as st
from typing import Literal, TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import AnyMessage
from langgraph.graph.schema import add_messages

# --- Define GameState structure ---
class GameState(TypedDict):
    messages: list[AnyMessage]
    number_to_guess: int
    word_list: list[str]
    word_to_guess: str
    _next: str


# --- Helper Functions ---
import random


def init_game_state() -> GameState:
    return {
        "messages": [],
        "number_to_guess": random.randint(1, 50),
        "word_list": ["apple", "chair", "elephant", "guitar", "rocket", "pencil", "pizza", "tiger"],
        "word_to_guess": random.choice(["apple", "chair", "elephant", "guitar", "rocket", "pencil", "pizza", "tiger"]),
        "_next": "menu"
    }


# --- Menu Node ---
def menu(state: GameState) -> GameState:
    st.title("🎮 Welcome to the Game Hub")
    st.write("Choose a game mode")

    game_mode = st.radio("Select a game:", ["Number Game", "Word Clue Guesser"])

    if game_mode == "Number Game":
        if st.button("Start Number Game"):
            state["_next"] = "start_number_game"
    elif game_mode == "Word Clue Guesser":
        if st.button("Start Word Clue Guesser"):
            state["_next"] = "start_word_game"

    return state


# --- Number Game Node ---
def number_game(state: GameState) -> GameState:
    st.subheader("Welcome to the Number Game!")
    st.write("Think of a number between 1 and 50, and I'll guess it.")

    if "guess" not in st.session_state:
        st.session_state.guess = random.randint(1, 50)
        st.session_state.attempts = 1

    guess = st.session_state.guess
    user_response = st.radio(f"Is your number {guess}?", ["greater", "less", "correct"], key=f"guess_{guess}")

    if user_response == "greater":
        st.session_state.guess += 1
        st.session_state.attempts += 1
    elif user_response == "less":
        st.session_state.guess -= 1
        st.session_state.attempts += 1
    elif user_response == "correct":
        st.success(f"Congrats! I guessed your number {guess} in {st.session_state.attempts} attempts.")
        state["_next"] = "menu"
        st.session_state.pop("guess", None)
        st.session_state.pop("attempts", None)
        return state

    state["_next"] = "start_number_game"
    return state


# --- Word Game Node ---
def word_game(state: GameState) -> GameState:
    st.subheader("Welcome to the Word Clue Guesser!")
    st.write("Choose a word from the following list:")
    st.json(state["word_list"])

    if "question" not in st.session_state:
        st.session_state.question_idx = 0
        st.session_state.questions = [
            "Is it a vehicle?",
            "Is it a living thing?",
            "Is it something found indoors?",
            "Is it edible?",
            "Is it used for writing?"
        ]
        st.session_state.answers = []

    if st.session_state.question_idx < len(st.session_state.questions):
        question = st.session_state.questions[st.session_state.question_idx]
        answer = st.radio(question, ["Yes", "No", "Maybe"], key=f"q_{st.session_state.question_idx}")
        st.session_state.answers.append((question, answer))
        if st.button("Next"):
            st.session_state.question_idx += 1
    else:
        st.success("Thanks for answering! I'm guessing... 🤔")
        st.write(f"My guess is: **{random.choice(state['word_list'])}**")
        if st.button("Return to menu"):
            st.session_state.clear()
            state["_next"] = "menu"
            return state

    state["_next"] = "start_word_game"
    return state


# --- Build LangGraph ---
builder = StateGraph(GameState)
builder.set_entry_point("menu")
builder.add_node("menu", menu)
builder.add_node("start_number_game", number_game)
builder.add_node("start_word_game", word_game)

builder.add_edge("menu", "start_number_game")
builder.add_edge("menu", "start_word_game")
builder.add_edge("start_number_game", "start_number_game")
builder.add_edge("start_number_game", "menu")
builder.add_edge("start_word_game", "start_word_game")
builder.add_edge("start_word_game", "menu")

app_graph = builder.compile()


# --- Streamlit app entry point ---
if "game_state" not in st.session_state:
    st.session_state.game_state = init_game_state()

st.session_state.game_state = app_graph.invoke(st.session_state.game_state)
