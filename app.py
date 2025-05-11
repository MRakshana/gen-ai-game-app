
#!/usr/bin/env python
# coding: utf-8

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import streamlit as st
from PIL import Image

# ----- Game State -----
class GameState(TypedDict):
    current_game: Optional[str]
    number_guess_min: int
    number_guess_max: int
    number_game_count: int
    word_game_count: int
    session_games: List[str]
    word_attempts: int
    target_word: Optional[str]
    possible_words: List[str]
    _next: str

# ----- Word Game Data -----
WORD_LIST = ["apple", "chair", "elephant", "guitar", "rocket", "pencil", "pizza", "tiger"]
CLUE_QUESTIONS = {
    "Is it a living thing?": lambda word: word in ["apple", "elephant", "tiger"],
    "Is it an animal?": lambda word: word in ["elephant", "tiger"],
    "Is it an object?": lambda word: word not in ["elephant", "tiger", "apple"],
    "Is it used in school?": lambda word: word in ["chair", "pencil"],
    "Is it a musical instrument?": lambda word: word == "guitar",
    "Is it edible?": lambda word: word in ["apple", "pizza"],
    "Does it have four legs?": lambda word: word in ["elephant", "tiger", "chair"],
    "Can it fly?": lambda word: word == "rocket"
}

# ----- Execution Tracker -----
class ExecutionTracker:
    def __init__(self):
        self.steps = []

    def track(self, state):
        self.steps.append({
            "node": state.get("_next", END),
            "game": state.get("current_game"),
            "action": f"Game: {state.get('current_game')}" if state.get("current_game") else "Menu"
        })
        return state

# ----- Game Agents -----
def game_selector_agent(state: GameState) -> GameState:
    st.header("🎮 Choose a Game")
    game_choice = st.radio("Select a game:", ("Number Game", "Word Game"))
    if game_choice == "Number Game":
        state["current_game"] = "number"
        state["_next"] = "start_number_game"
    else:
        state["current_game"] = "word"
        state["_next"] = "start_word_game"
    return state

def number_game_agent(state: GameState) -> GameState:
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)

    if col1.button("Yes"):
        state["number_guess_min"] = mid + 1
    elif col2.button("No"):
        state["number_guess_max"] = mid

    if state["number_guess_min"] >= state["number_guess_max"]:
        st.success(f"🎯 Your number is {state['number_guess_min']}! I guessed it!")
        state["number_game_count"] += 1
        state["session_games"].append("number")
        state["number_guess_min"] = 1
        state["number_guess_max"] = 50
        state["_next"] = "menu"
    else:
        state["_next"] = "start_number_game"

    return state

def word_game_agent(state: GameState) -> GameState:
    if not state["possible_words"]:
        state["possible_words"] = WORD_LIST.copy()
        state["target_word"] = st.text_input("Enter your secret word:", key="target_word")
        st.info("Think of a word from this list: " + ", ".join(WORD_LIST))

    questions = list(CLUE_QUESTIONS.keys())
    if state["word_attempts"] < len(questions):
        question = questions[state["word_attempts"]]
        st.write(question)
        col1, col2 = st.columns(2)

        answer = None
        if col1.button("Yes"):
            answer = "yes"
        elif col2.button("No"):
            answer = "no"

        if answer:
            predicate = CLUE_QUESTIONS[question]
            state["possible_words"] = [
                word for word in state["possible_words"]
                if (predicate(word) and answer == "yes") or
                   (not predicate(word) and answer == "no")
            ]
            state["word_attempts"] += 1

    if len(state["possible_words"]) == 1:
        guess = state["possible_words"][0]
        st.write(f"My guess is: **{guess}**")
        correct = st.radio("Am I right?", ("Yes", "No"))
        if correct == "Yes":
            st.success("Yay! I guessed your word!")
        else:
            st.warning("Oops! Let me try again.")
        state["word_game_count"] += 1
        state["session_games"].append("word")
        state["possible_words"] = []
        state["_next"] = "menu"
    else:
        state["_next"] = "start_word_game"

    return state

# ----- Router -----
def router(state: GameState) -> str:
    return state.get("_next", END)

# ----- Main App -----
def main():
    st.set_page_config(page_title="GenAI Game App", layout="centered")
    st.title("🧠 GenAI Multi-Game App")
    st.markdown("Choose and play one of the two games: Number Guess or Word Guess.")

    tracker = ExecutionTracker()

    initial_state: GameState = {
        "current_game": None,
        "number_guess_min": 1,
        "number_guess_max": 50,
        "number_game_count": 0,
        "word_game_count": 0,
        "session_games": [],
        "word_attempts": 0,
        "target_word": None,
        "possible_words": [],
        "_next": "menu"
    }

    builder = StateGraph(GameState)
    builder.add_node("menu", lambda state: tracker.track(game_selector_agent(state)))
    builder.add_node("start_number_game", lambda state: tracker.track(number_game_agent(state)))
    builder.add_node("start_word_game", lambda state: tracker.track(word_game_agent(state)))

    builder.set_entry_point("menu")
    builder.add_conditional_edges("menu", router)
    builder.add_conditional_edges("start_number_game", router)
    builder.add_conditional_edges("start_word_game", router)

    app = builder.compile()
    final_state = app.invoke(initial_state)

    st.markdown("---")
    st.subheader("🧾 Final Game State")
    for key, value in final_state.items():
        st.write(f"**{key}**: {value}")

# ---- Run Streamlit App ----
main()
