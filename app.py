import streamlit as st
from typing import Dict, Any, List

# Define GameState type alias
GameState = Dict[str, Any]

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

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = 0
if 'number_game_count' not in st.session_state:
    st.session_state['number_game_count'] = 0
if 'word_game_count' not in st.session_state:
    st.session_state['word_game_count'] = 0

st.session_state['session_id'] += 1

# Select Game
game_choice = st.radio("Choose a game to play:", ["Number Game", "Word Game"], key=f"game_choice_{st.session_state['session_id']}")

if game_choice == "Number Game":
    # Number Guessing Game
    if 'min_val' not in st.session_state:
        st.session_state['min_val'] = 1
        st.session_state['max_val'] = 50

    min_val = st.session_state['min_val']
    max_val = st.session_state['max_val']
    mid = (min_val + max_val) // 2
    st.write(f"Is your number greater than {mid}?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes", key=f"number_game_yes_{st.session_state['session_id']}_{st.session_state['number_game_count']}_{mid}"):
            st.session_state['min_val'] = mid + 1
    with col2:
        if st.button("No", key=f"number_game_no_{st.session_state['session_id']}_{st.session_state['number_game_count']}_{mid}"):
            st.session_state['max_val'] = mid

    if st.session_state['min_val'] == st.session_state['max_val']:
        st.success(f"Your number is {st.session_state['min_val']}! I guessed it!")
        st.session_state['number_game_count'] += 1
        st.session_state['min_val'] = 1
        st.session_state['max_val'] = 50

elif game_choice == "Word Game":
    if 'word_attempts' not in st.session_state:
        st.session_state['word_attempts'] = 0
        st.session_state['possible_words'] = WORD_LIST.copy()

    if st.session_state['word_attempts'] == 0:
        st.session_state['target_word'] = st.text_input("Enter your secret word (testing purpose):", key="target_word")
        st.write(f"Choose from: {', '.join(WORD_LIST)}")

    question_keys = list(CLUE_QUESTIONS.keys())
    if st.session_state['word_attempts'] < len(question_keys):
        question = question_keys[st.session_state['word_attempts']]
        st.write(question)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes", key=f"yes_{st.session_state['session_id']}_{st.session_state['word_attempts']}"):
                answer = "yes"
            else:
                answer = None
        with col2:
            if st.button("No", key=f"no_{st.session_state['session_id']}_{st.session_state['word_attempts']}"):
                answer = "no"
            else:
                answer = None

        if answer:
            predicate = CLUE_QUESTIONS[question]
            st.session_state['possible_words'] = [
                word for word in st.session_state['possible_words']
                if (predicate(word) and answer == "yes") or (not predicate(word) and answer == "no")
            ]
            st.session_state['word_attempts'] += 1

    if len(st.session_state['possible_words']) == 1:
        guess = st.session_state['possible_words'][0]
        st.success(f"I think your word is: {guess}")
        correct = st.radio("Am I right?", ["Yes", "No"], key="word_guess_check")
        if correct == "Yes":
            st.session_state['word_game_count'] += 1
            st.session_state['word_attempts'] = 0
            st.session_state['possible_words'] = WORD_LIST.copy()
        elif correct == "No":
            st.warning("Hmm. Let me try again.")
            st.session_state['word_attempts'] = 0
            st.session_state['possible_words'] = WORD_LIST.copy()

st.write("\n---\n")
st.write(f"Number games played: {st.session_state['number_game_count']}")
st.write(f"Word games played: {st.session_state['word_game_count']}")
