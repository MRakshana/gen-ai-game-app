import streamlit as st
import random

# Define the global counters
number_game_counter = 0
word_game_counter = 0

# List of words for the Word Clue Guesser game
word_list = ["apple", "chair", "elephant", "guitar", "rocket", "pencil", "pizza", "tiger"]

# 1. Number Game - Binary Search Logic
def number_game():
    global number_game_counter
    st.write("Welcome to the Number Game!")
    st.write("Think of a number between 1 and 50, and I'll guess it.")
    
    low, high = 1, 50
    attempts = 0
    guessed_number = None
    
    while guessed_number != "correct" and low <= high:
        # Guessing number based on binary search
        guess = (low + high) // 2
        attempts += 1
        guessed_number = st.radio(f"Is your number {guess}?", ["greater", "less", "correct"])

        if guessed_number == "greater":
            low = guess + 1
        elif guessed_number == "less":
            high = guess - 1

    number_game_counter += 1
    st.write(f"Congrats! I guessed your number {guess} in {attempts} attempts.")
    st.write(f"Number Game counter: {number_game_counter}")
    st.write("Returning to the main menu...")

# 2. Word Clue Guesser Game
def word_clue_guesser():
    global word_game_counter
    st.write("Welcome to the Word Clue Guesser!")
    st.write("Choose a word from the following list:")
    st.write(word_list)

    word_to_guess = random.choice(word_list)
    questions_asked = 0
    max_questions = 5
    correct_guess = False
    user_input = ""

    # Ask descriptive yes/no/maybe questions
    while questions_asked < max_questions and not correct_guess:
        question = f"Is it a {random.choice(['fruit', 'object', 'animal', 'food', 'vehicle'])}?"
        answer = st.radio(question, ["Yes", "No", "Maybe"], key=f"question_{questions_asked}")

        if answer == "Yes":
            user_input = "Yes"
        elif answer == "Maybe":
            user_input = "Maybe"
        else:
            user_input = "No"
        
        # After asking questions, try to guess the word
        if questions_asked == max_questions - 1:
            guess = word_to_guess  # This is simple for now, can be improved
            correct_guess = (guess.lower() == word_to_guess.lower())
            break

        questions_asked += 1

    if correct_guess:
        st.write(f"Success! I guessed the word: {word_to_guess}.")
    else:
        retry = st.radio("I couldn't guess the word. Would you like to try again?", ["Yes", "No"], key="retry")
        if retry == "Yes":
            word_clue_guesser()
        else:
            st.write("Returning to the main menu...")

    word_game_counter += 1
    st.write(f"Word Game counter: {word_game_counter}")
    st.write("Returning to the main menu...")

# Main Menu UI
def main_menu():
    game_mode = st.radio("Choose a game mode", ["Number Game", "Word Clue Guesser"])

    if game_mode == "Number Game":
        if st.button("Start Number Game"):
            number_game()

    elif game_mode == "Word Clue Guesser":
        if st.button("Start Word Clue Guesser"):
            word_clue_guesser()

# Display the Main Menu
st.title("Welcome to the Game Hub")
main_menu()

 
