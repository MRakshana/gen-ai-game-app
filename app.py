import streamlit as st
from typing import List, Optional
from graphviz import Digraph
from PIL import Image # to display images
from io import BytesIO # to work with image data

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

# ------------------ HELPER FUNCTIONS ------------------ #
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

    # Save the graph to a file
    dot.render('game_state_machine', format='png', cleanup=True)

    # Display the image
    try:
        img = Image.open('game_state_machine.png')
        st.image(img)
    except FileNotFoundError:
        st.error("Graph visualization not available.")


# ------------------ MAIN APP ------------------ #
def main():
    st.title("Interactive Games")

    # Initialize session state (this is crucial for Streamlit!)
    if "current_game" not in st.session_state:
        st.session_state.current_game = None
        st.session_state.number_guess_min = 1
        st.session_state.number_guess_max = 50
        st.session_state.number_game_count = 0
        st.session_state.word_game_count = 0
        st.session_state.session_games = []
        st.session_state.word_attempts = 0
        st.session_state.target_word = None
        st.session_state.possible_words = WORD_LIST.copy()

    # Visualization (show at the top)
    st.header("Game Flow Visualization")
    visualize_structure_enhanced()

    # Game Selection Menu
    if st.session_state.current_game is None:
        st.header("Choose a Game")
        game_choice = st.radio("Select a game:", ("Number Game", "Word Game"))

        if game_choice == "Number Game":
            st.session_state.current_game = "number"
        elif game_choice == "Word Game":
            st.session_state.current_game = "word"

    # Number Game
    if st.session_state.current_game == "number":
        st.header("Number Guessing Game")
        number_game()

    # Word Game
    elif st.session_state.current_game == "word":
        st.header("Word Clue Game")
        word_game()

    # Play Again?
    if st.session_state.current_game in ["number_over", "word_over"]:
        st.header("Play Again?")
        play_again = st.radio("Do you want to play again?", ("Yes", "No"))
        if play_again == "Yes":
            st.session_state.current_game = None # Reset to game selection
            st.session_state.number_guess_min = 1
            st.session_state.number_guess_max = 50
            st.session_state.word_attempts = 0
            st.session_state.possible_words = WORD_LIST.copy()
            st.session_state.target_word = None
        else:
            st.write("Thanks for playing!")

def number_game():
    min_val = st.session_state.number_guess_min
    max_val = st.session_state.number_guess_max
    mid = (min_val + max_val) // 2

    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes"):
            st.session_state.number_guess_min = mid + 1
            if st.session_state.number_guess_min == st.session_state.number_guess_max:
                st.write(f"Your number is {st.session_state.number_guess_min}! I guessed it!")
                st.session_state.number_game_count += 1
                st.session_state.session_games.append("number")
                st.session_state.current_game = "number_over" # Go to play again
            else:
                st.rerun() # Rerun the script to ask again
    with col2:
        if st.button("No"):
            st.session_state.number_guess_max = mid
            if st.session_state.number_guess_min == st.session_state.number_guess_max:
                st.write(f"Your number is {st.session_state.number_guess_min}! I guessed it!")
                st.session_state.number_game_count += 1
                st.session_state.session_games.append("number")
                st.session_state.current_game = "number_over" # Go to play again
            else:
                st.rerun() # Rerun the script to ask again

def word_game():
    if "possible_words" not in st.session_state or st.session_state.possible_words is None:
        st.session_state.possible_words = WORD_LIST.copy()
        st.session_state.target_word = st.text_input("Enter your secret word (for testing purposes):", key="target_word_input") # Keep secret for now
        st.write("Think of a word from this list:")
        st.write(", ".join(WORD_LIST))


    if st.session_state.word_attempts < len(CLUE_QUESTIONS):
        questions = list(CLUE_QUESTIONS.keys())
        question_idx = st.session_state.word_attempts
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

            for word in st.session_state.possible_words:
                try:
                    if predicate(word) and answer == "yes":
                        filtered_words.append(word)
                    elif not predicate(word) and answer == "no":
                        filtered_words.append(word)
                except Exception as e:
                    st.error(f"Error evaluating clue for '{word}': {e}")
                    continue

            st.session_state.possible_words = filtered_words
            st.session_state.word_attempts += 1

            if len(filtered_words) == 1:
                guess = filtered_words[0]
                st.write(f"\nI think your word is: **{guess}**")
                correct = st.radio("Am I right?", ("Yes", "No"), key="correct_guess")

                if correct == "Yes":
                    st.write("Yay! I guessed your word!")
                    st.session_state.word_game_count += 1
                    st.session_state.session_games.append("word")
                    st.session_state.current_game = "word_over" # Go to play again
                elif correct == "No":
                    st.write("Hmm, let me try again.")
                    st.session_state.possible_words = WORD_LIST.copy()
                    st.session_state.word_attempts = 0
                    st.rerun() # Restart the game
            elif len(filtered_words) == 0:
                st.write("No matching words found. Let's start over.")
                st.session_state.possible_words = WORD_LIST.copy()
                st.session_state.word_attempts = 0
                st.rerun() # Restart the game
            else:
                st.rerun() # Continue guessing
    else:
        if len(st.session_state.possible_words) > 1:
            guess = st.session_state.possible_words[0]
            st.write(f"\nMy best guess is: **{guess}**")
        elif len(st.session_state.possible_words) == 1:
            guess = st.session_state.possible_words[0]
            st.write(f"\nMy guess is: **{guess}**")
        else:
            st.write("I couldn't guess the word.")
            guess = "" # To avoid errors later

        correct = st.radio("Am I right?", ("Yes", "No"), key="final_guess")
        if correct == "Yes":
            st.write("Yay! I guessed your word!")
            st.session_state.word_game_count += 1
            st.session_state.session_games.append("word")
            st.session_state.current_game = "word_over" # Go to play again
        elif correct == "No":
            st.write(f"Oops! The correct word was: **{st.session_state.target_word}**")
            st.session_state.word_game_count += 1
            st.session_state.session_games.append("word")
            st.session_state.current_game = "word_over" # Go to play again


if __name__ == "__main__":
    main()





