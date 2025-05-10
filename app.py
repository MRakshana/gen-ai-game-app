#!/usr/bin/env python
# coding: utf-8

from __future__ import annotations  # Enables forward references for type hints
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import streamlit as st
from PIL import Image
import os

# ---------------------------- Game State ----------------------------
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

# ------------------------ Constants ------------------------
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

# ------------------------ Execution Tracker ------------------------
class ExecutionTracker:
    def __init__(self):
        self.steps = []
        self.current_state = None

    def track(self, state):
        self.current_state = state.get("_next", END)
        self.steps.append({
            "node": self.current_state,
            "game": state.get("current_game"),
            "action": f"Game: {state.get('current_game')}" if state.get("current_game") else "Menu"
        })
        return state

# ------------------------ Game Agents ------------------------
def game_selector_agent(state: GameState) -> GameState:
    st.header("Choose a Game")
    game_choice = st.radio("Select a game:", ("Number Game", "Word Game"), key="game_choice")
    if game_choice == "Number Game":
        state["current_game"] = "number"
        state["_next"] = "start_number_game"
    elif game_choice == "Word Game":
        state["current_game"] = "word"
        state["_next"] = "start_word_game"
    else:
        state["_next"] = END
    return state

def number_game_agent(state: GameState) -> GameState:
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)

    session_id = st.session_state.get('session_id', 0)
    game_id = state["number_game_count"]

    with col1:
        if st.button("Yes", key=f"number_game_yes_{session_id}_{game_id}_{mid}"):
            state["number_guess_min"] = mid + 1
            if state["number_guess_min"] == state["number_guess_max"]:
                st.success(f"Your number is {state['number_guess_min']}! I guessed it!")
                state["number_game_count"] += 1
                state["session_games"].append("number")
                state["number_guess_min"] = 1
                state["number_guess_max"] = 50
                state["_next"] = "menu"
            else:
                state["_next"] = "start_number_game"

    with col2:
        if st.button("No", key=f"number_game_no_{session_id}_{game_id}_{mid}"):
            state["number_guess_max"] = mid
            if state["number_guess_min"] == state["number_guess_max"]:
                st.success(f"Your number is {state['number_guess_min']}! I guessed it!")
                state["number_game_count"] += 1
                state["session_games"].append("number")
                state["number_guess_min"] = 1
                state["number_guess_max"] = 50
                state["_next"] = "menu"
            else:
                state["_next"] = "start_number_game"

    return state

def word_game_agent(state: GameState) -> GameState:
    session_id = st.session_state.get('session_id', 0)
    word_game_id = state["word_game_count"]

    if "possible_words" not in state or state["possible_words"] is None:
        state["possible_words"] = WORD_LIST.copy()
        state["target_word"] = st.text_input("Enter your secret word (for testing purposes):", key=f"target_word_{word_game_id}")
        st.write("Think of a word from this list:")
        st.write(", ".join(WORD_LIST))

    if state["word_attempts"] < len(CLUE_QUESTIONS):
        questions = list(CLUE_QUESTIONS.keys())
        question_idx = state["word_attempts"]
        question = questions[question_idx]

        st.write(question)
        col1, col2 = st.columns(2)
        answer = None

        with col1:
            if st.button("Yes", key=f"word_yes_{session_id}_{word_game_id}_{question_idx}"):
                answer = "yes"
        with col2:
            if st.button("No", key=f"word_no_{session_id}_{word_game_id}_{question_idx}"):
                answer = "no"

        if answer:
            predicate = CLUE_QUESTIONS[question]
            filtered_words = []

            for word in state["possible_words"]:
                try:
                    if predicate(word) and answer == "yes":
                        filtered_words.append(word)
                    elif not predicate(word) and answer == "no":
                        filtered_words.append(word)
                except Exception as e:
                    st.error(f"Error with word '{word}': {e}")

            state["possible_words"] = filtered_words
            state["word_attempts"] += 1

            if len(filtered_words) == 1:
                guess = filtered_words[0]
                st.write(f"\nI think your word is: **{guess}**")
                correct = st.radio("Am I right?", ("Yes", "No"), key=f"word_guess_correct_{word_game_id}")
                if correct == "Yes":
                    st.success("Yay! I guessed your word!")
                    state["word_game_count"] += 1
                    state["session_games"].append("word")
                    state["possible_words"] = None
                    state["_next"] = "menu"
                else:
                    st.warning("Let's try again!")
                    state["possible_words"] = WORD_LIST.copy()
                    state["word_attempts"] = 0
                    state["_next"] = "start_word_game"
            elif len(filtered_words) == 0:
                st.error("No words match! Let's start over.")
                state["possible_words"] = WORD_LIST.copy()
                state["word_attempts"] = 0
                state["_next"] = "start_word_game"
        else:
            st.info("Waiting for your answer...")

    return state

# ------------------------ Router ------------------------
def router(state: GameState) -> str:
    return state.get("_next", END)

# ------------------------ Visualizer Placeholders ------------------------
def visualize_structure():
    st.header("Game State Machine Structure")
    st.write("Graph visualization is not available in this deployed version.")

def visualize_execution(execution_steps):
    st.header("Execution Trace")
    st.write("Execution trace visualization is not available in this deployed version.")

# ------------------------ Debug State Print ------------------------
def print_game_state(state: GameState):
    st.write("Final Game State:")
    for key, value in state.items():
        st.write(f"{key}: {value}")

# ------------------------ Main App ------------------------
def main():
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
        "possible_words": None,
        "_next": "menu"
    }

    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = 0
    st.session_state['session_id'] += 1

    builder = StateGraph(GameState)

    builder.add_node("menu", lambda state: tracker.track(game_selector_agent(state)))
    builder.add_node("start_number_game", lambda state: tracker.track(number_game_agent(state)))
    builder.add_node("start_word_game", lambda state: tracker.track(word_game_agent(state)))

    builder.set_entry_point("menu")

    builder.add_conditional_edges("menu", router)
    builder.add_conditional_edges("start_number_game", router)
    builder.add_conditional_edges("start_word_game", router)

    app = builder.compile()

    visualize_structure()

    st.write("🎮 Welcome to the Gen AI Game App!")
    final_state = app.invoke(initial_state)

    visualize_execution(tracker.steps)
    print_game_state(final_state)

if __name__ == "__main__":
    if "DISPLAY" not in os.environ:
        main()
