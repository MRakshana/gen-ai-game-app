from typing import Dict, Any

# Define GameState as a dictionary with a flexible structure
GameState = Dict[str, Any]

# Sample default state initialization (optional, for demonstration)
def initialize_game_state() -> GameState:
    return {
        "number_guess_min": 1,
        "number_guess_max": 50,
        "number_game_count": 0,
        "word_game_count": 0,
        "word_attempts": 0,
        "possible_words": None,
        "session_games": [],
        "_next": "menu",
        "target_word": "",
    }

def number_game_agent(state: GameState) -> GameState:
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)
    session_id = st.session_state.get('session_id', 0)
    with col1:
        if st.button(f"Yes_{session_id}_{state['number_game_count']}", key=f"number_game_yes_{session_id}_{state['number_game_count']}"):
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
        if st.button(f"No_{session_id}_{state['number_game_count']}", key=f"number_game_no_{session_id}_{state['number_game_count']}"):
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
    if "possible_words" not in state or state["possible_words"] is None:
        state["possible_words"] = WORD_LIST.copy()
        state["target_word"] = st.text_input("Enter your secret word (for testing purposes):", key="target_word_input")
        st.write("Think of a word from this list:")
        st.write(", ".join(WORD_LIST))

    if state["word_attempts"] < len(CLUE_QUESTIONS):
        questions = list(CLUE_QUESTIONS.keys())
        question_idx = state["word_attempts"]
        question = questions[question_idx]
        st.write(question)
        col1, col2 = st.columns(2)
        session_id = st.session_state.get('session_id', 0)
        with col1:
            if st.button(f"Yes_{question_idx}_{session_id}_{state['word_game_count']}_{state['word_attempts']}", key=f"yes_{question_idx}_{session_id}_{state['word_game_count']}_{state['word_attempts']}"):
                answer = "yes"
            else:
                answer = None
        with col2:
            if st.button(f"No_{question_idx}_{session_id}_{state['word_game_count']}_{state['word_attempts']}", key=f"no_{question_idx}_{session_id}_{state['word_game_count']}_{state['word_attempts']}"):
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
                guess = filtered_words[0]
                st.write(f"\nI think your word is: **{guess}**")
                correct = st.radio("Am I right?", ("Yes", "No"), key=f"correct_guess_{session_id}")

                if correct == "Yes":
                    st.write("Yay! I guessed your word!")
                    state["word_game_count"] += 1
                    state["session_games"].append("word")
                    state["possible_words"] = None
                    state["_next"] = "menu"
                elif correct == "No":
                    st.write("Hmm, let me try again.")
                    state["possible_words"] = WORD_LIST.copy()
                    state["word_attempts"] = 0
                    state["_next"] = "start_word_game"
                elif len(filtered_words) == 0:
                    st.write("No matching words found. Let's start over.")
                    state["possible_words"] = WORD_LIST.copy()
                    state["word_attempts"] = 0
                    state["_next"] = "start_word_game"
                else:
                    state["_next"] = "start_word_game"
        else:
            if len(state["possible_words"]) > 1:
                guess = state["possible_words"][0]
                st.write(f"\nMy best guess is: **{guess}**")
            elif len(state["possible_words"]) == 1:
                guess = state["possible_words"][0]
                st.write(f"\nMy guess is: **{guess}**")
            else:
                st.write("I couldn't guess the word.")
                guess = ""

            correct = st.radio(f"Am I right?_{session_id}", ("Yes", "No"), key=f"final_guess_{session_id}")
            if correct == "Yes":
                st.write("Yay! I guessed your word!")
                state["word_game_count"] += 1
                state["session_games"].append("word")
                state["possible_words"] = None
                state["_next"] = "menu"
            elif correct == "No":
                st.write(f"Oops! The correct word was: **{state['target_word']}**")
                state["word_game_count"] += 1
                state["session_games"].append("word")
                state["possible_words"] = None
                state["_next"] = "menu"

    return state
