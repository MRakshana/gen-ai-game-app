#!/usr/bin/env python
# coding: utf-8

# ### Objective

# The objective of the code is to create a CLI-based game application offering two interactive games: a Number Guessing Game and a Word Clue Game. The Number Guessing Game allows the system to guess a number based on user feedback. The Word Clue Game provides clues to guess a word. After each game, the user can choose to play again or exit. The system manages user input and game flow, providing a seamless experience between games

# In[3]:

from graphviz import Digraph
# from IPython.display import Image, display # Commented out IPython import

def visualize_structure_enhanced():
    dot = Digraph(comment='Enhanced Game State Machine', graph_attr={'rankdir': 'LR'}) # Layout from Left to Right

    # Define node styles
    start_end_style = {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'lightgreen'}
    game_state_style = {'shape': 'rectangle', 'style': 'rounded'}
    decision_style = {'shape': 'diamond', 'style': 'filled', 'fillcolor': 'lightblue'}

    # Define the states with styles
    dot.node('start', 'Start', **start_end_style)
    dot.node('choose_game', 'Choose Game', **decision_style)
    dot.node('start_number_game', 'Start Number Game', **game_state_style)
    dot.node('number_guessing', 'Number Guessing', **game_state_style)
    dot.node('number_game_over', 'Number Game Over', **game_state_style)
    dot.node('start_word_game', 'Start Word Game', **game_state_style)
    dot.node('word_guessing', 'Word Guessing', **game_state_style)
    dot.node('word_game_over', 'Word Game Over', **game_state_style)
    dot.node('play_again', 'Play Again?', **decision_style)
    dot.node('end', 'End', **start_end_style)

    # Define edge styles and labels
    dot.edge('start', 'choose_game', label='Begin')
    dot.edge('choose_game', 'start_number_game', label='Select Number Game', color='blue')
    dot.edge('choose_game', 'start_word_game', label='Select Word Game', color='green')
    dot.edge('start_number_game', 'number_guessing', label='Start Guessing')
    dot.edge('number_guessing', 'number_guessing', label='Incorrect Guess', style='dashed')
    dot.edge('number_guessing', 'number_game_over', label='Correct/Out of Attempts', color='red')
    dot.edge('start_word_game', 'word_guessing', label='Start Guessing')
    dot.edge('word_guessing', 'word_guessing', label='Incorrect Guess', style='dashed')
    dot.edge('word_guessing', 'word_game_over', label='Correct/Out of Attempts', color='red')
    dot.edge('number_game_over', 'play_again', label='Yes')
    dot.edge('word_game_over', 'play_again', label='Yes')
    dot.edge('play_again', 'choose_game', label='Yes', style='bold')
    dot.edge('play_again', 'end', label='No')
    dot.edge('start_number_game', 'start_number_game', label='Continue setup', style='dotted', color='gray')
    dot.edge('start_word_game', 'start_word_game', label='Continue setup', style='dotted', color='gray')

    # display(Image(dot.pipe(format='png'))) # Commented out display
    dot.render('game_state_machine', format='png', cleanup=True) # Save the graph to a file
    return dot

if __name__ == "__main__":
    visualize_structure_enhanced()


# - Dual Game Selection: The user chooses between "Number Game" (blue path) and "Word Game" (green path) at the start.
# - Iterative Guessing Loops: Both games feature a "Guessing" state with a self-loop for incorrect attempts, allowing multiple tries.
# - Clear End Conditions: Each game ends in a "Game Over" state (red path) triggered by a correct guess or exhaustion of attempts.
# - Play Again Option: A "Yes" transition from both "Game Over" states (curved black arrow) indicates the possibility to return to the initial game selection.

# In[12]:

# pip install networkx matplotlib # This line is commented out


# In[1]:


from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from graphviz import Digraph
# from IPython.display import display, Image # Commented out IPython import
import streamlit as st # Added streamlit import
from PIL import Image # to display images

# ------------------ GAME STATE ------------------ #
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

# ------------------ GLOBALS ------------------ #
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

# ------------------ EXECUTION TRACKER ------------------ #
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

# ------------------ AGENTS ------------------ #
def game_selector_agent(state: GameState) -> GameState:
    # print("\nMain Menu:\n1. Number Game\n2. Word Game\n3. Exit")
    # choice = input("Choose a game (1/2) or Exit (3): ").strip()
    # if choice == "1":
    #     state["current_game"] = "number"
    #     state["_next"] = "start_number_game"
    # elif choice == "2":
    #     state["current_game"] = "word"
    #     state["_next"] = "start_word_game"
    # else:
    #     state["_next"] = END
    # return state

    st.header("Choose a Game")
    game_choice = st.radio("Select a game:", ("Number Game", "Word Game"))

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
    # min_val = state["number_guess_min"]
    # max_val = state["number_guess_max"]
    # mid = (min_val + max_val) // 2

    # response = input(f"Is your number greater than {mid}? (yes/no): ").strip().lower()
    # if response == "yes":
    #     state["number_guess_min"] = mid + 1
    # else:
    #     state["number_guess_max"] = mid

    # if state["number_guess_min"] == state["number_guess_max"]:
    #     print(f"\nYour number is {state['number_guess_min']}! I guessed it!")
    #     state["number_game_count"] += 1
    #     state["session_games"].append("number")
    #     state["number_guess_min"] = 1
    #     state["number_guess_max"] = 50
    #     state["_next"] = "menu"
    # else:
    #     state["_next"] = "start_number_game"
    # return state

    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes"):
            state["number_guess_min"] = mid + 1
            if state["number_guess_min"] == state["number_guess_max"]:
                st.write(f"Your number is {state['number_guess_min']}! I guessed it!")
                state["number_game_count"] += 1
                state["session_games"].append("number")
                state["number_guess_min"] = 1
                state["number_guess_max"] = 50
                state["_next"] = "menu"
            else:
                state["_next"] = "start_number_game"
    with col2:
        if st.button("No"):
            state["number_guess_max"] = mid
            if state["number_guess_min"] == state["number_guess_max"]:
                st.write(f"Your number is {state['number_guess_min']}! I guessed it!")
                state["number_game_count"] += 1
                state["session_games"].append("number")
                state["number_guess_min"] = 1
                state["number_guess_max"] = 50
                state["_next"] = "menu"
            else:
                state["_next"] = "start_number_game"
    return state

def word_game_agent(state: GameState) -> GameState:
    # if "possible_words" not in state or state["possible_words"] is None:
    #     state["possible_words"] = WORD_LIST.copy()

    # if "target_word" not in state or state["target_word"] is None:
    #     print("Think of a word from this list:")
    #     print(", ".join(WORD_LIST))
    #     state["target_word"] = input("Enter your secret word (for testing purposes): ").strip().lower()

    # if state["word_attempts"] < len(CLUE_QUESTIONS):
    #     questions = list(CLUE_QUESTIONS.keys())
    #     question_idx = state["word_attempts"]
    #     question = questions[question_idx]
    #     answer = input(f"{question} (yes/no): ").strip().lower()

    #     predicate = CLUE_QUESTIONS[question]
    #     filtered_words = []

    #     for word in state["possible_words"]:
    #         try:
    #             if predicate(word) and answer == "yes":
    #                 filtered_words.append(word)
    #             elif not predicate(word) and answer == "no":
    #                 filtered_words.append(word)
    #         except Exception as e:
    #             print(f"Error evaluating clue for '{word}': {e}")
    #             continue

    #     state["possible_words"] = filtered_words
    #     state["word_attempts"] += 1

    #     if len(filtered_words) == 1:
    #         guess = filtered_words[0]
    #         print(f"\nI think your word is: **{guess}**")
    #         correct = input("Am I right? (yes/no): ").strip().lower()
    #         if correct == "yes":
    #             print("Yay! I guessed your word!")
    #             state["word_game_count"] += 1
    #             state["session_games"].append("word")
    #             state["possible_words"] = None
    #             state["_next"] = "menu"
    #         else:
    #             print("Hmm, let me try again.")
    #             state["possible_words"] = WORD_LIST.copy()
    #             state["word_attempts"] = 0
    #             state["_next"] = "start_word_game"
    #     elif len(filtered_words) == 0:
    #         print("No matching words found. Let's start over.")
    #         state["possible_words"] = WORD_LIST.copy()
    #         state["word_attempts"] = 0
    #         state["_next"] = "start_word_game"
    #     else:
    #         state["_next"] = "start_word_game"
    # else:
    #     if len(state["possible_words"]) > 1:
    #         guess = state["possible_words"][0]
    #         print(f"\nMy best guess is: **{guess}**")
    #     else:
    #         guess = state["possible_words"][0]
    #         print(f"\nMy guess is: **{guess}**")

    #     correct = input("Am I right? (yes/no): ").strip().lower()
    #     state["word_game_count"] += 1
    #     state["session_games"].append("word")

    #     if correct == "yes":
    #         print("Yay! I guessed your word!")
    #     else:
    #         print(f"Oops! The correct word was: **{state['target_word']}**")

    #     state["possible_words"] = None
    #     state["_next"] = "menu"

    # return state

    if "possible_words" not in state or state["possible_words"] is None:
        state["possible_words"] = WORD_LIST.copy()
        state["target_word"] = st.text_input("Enter your secret word (for testing purposes):", key="target_word_input")  # Keep secret for now
        st.write("Think of a word from this list:")
        st.write(", ".join(WORD_LIST))

    if state["word_attempts"] < len(CLUE_QUESTIONS):
        questions = list(CLUE_QUESTIONS.keys())
        question_idx = state["word_attempts"]
        question = questions[question_idx]
        st.write(question)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes", key=f"yes_{question_idx}"):
                answer = "yes"
            else:
                answer = None
        with col2:
            if st.button("No", key=f"no_{question_idx}"):
                answer = "no"
            else:
                answer = None

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
                    st.error(f"Error evaluating clue for '{word}': {e}")
                    continue

            state["possible_words"] = filtered_words
            state["word_attempts"] += 1

            if len(filtered_words) == 1:
                guess = filtered_words
