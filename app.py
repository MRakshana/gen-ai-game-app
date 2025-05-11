import streamlit as st
from langgraph.graph import StateGraph
from typing import TypedDict
from typing_extensions import Annotated

# Define GameState TypedDict with Annotated to handle multiple values for '_next'
class GameState(TypedDict):
    _next: Annotated[str, "next_step"]  # Define '_next' as a single value key for each step
    number_guess_min: int
    number_guess_max: int
    number_game_count: int
    word_game_count: int
    session_games: list[str]

# Initialize the state with default values
def initialize_state() -> GameState:
    return {
        "_next": "menu",  # Direct string value instead of Annotated
        "number_guess_min": 1,
        "number_guess_max": 50,
        "number_game_count": 0,
        "word_game_count": 0,
        "session_games": [],
    }

# Menu agent
def menu(state: GameState) -> GameState:
    st.title("🧠 Gen AI Game App")
    st.subheader("Choose a game")
    col1, col2 = st.columns(2)

    if col1.button("Play Number Guessing Game"):
        state["_next"] = "start_number_game"
    elif col2.button("Play Word Clue Game"):
        state["_next"] = "start_word_game"

    return state

# Number guessing game agent
def number_game_agent(state: GameState) -> GameState:
    min_val = state.get("number_guess_min", 1)
    max_val = state.get("number_guess_max", 50)
    mid = (min_val + max_val) // 2

    st.subheader("🔢 Number Guessing Game")
    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)

    user_input = None
    if col1.button("Yes"):
        user_input = "yes"
    elif col2.button("No"):
        user_input = "no"

    # Apply user response if present
    if user_input == "yes":
        state["number_guess_min"] = mid + 1
    elif user_input == "no":
        state["number_guess_max"] = mid

    # Check if number is guessed
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

# Word guessing game agent
def word_game_agent(state: GameState) -> GameState:
    st.subheader("🧩 Word Clue Game")
    st.write("Clue: It's a large animal with a trunk.")
    answer = st.text_input("Your Guess:", key="word_game_input")

    if answer:
        if answer.lower() == "elephant":
            st.success("Correct! 🎉")
            state["word_game_count"] += 1
            state["session_games"].append("word")
            state["_next"] = "menu"
        else:
            st.warning("Try again!")
            state["_next"] = "start_word_game"
    else:
        state["_next"] = "start_word_game"

    return state

# Graph creation with explicit next-step handling
def create_game_graph():
    builder = StateGraph(GameState)
    builder.add_node("menu", menu)
    builder.add_node("start_number_game", number_game_agent)
    builder.add_node("start_word_game", word_game_agent)
    builder.set_entry_point("menu")
    builder.add_edge("menu", "start_number_game")
    builder.add_edge("menu", "start_word_game")
    builder.add_edge("start_number_game", "start_number_game")
    builder.add_edge("start_number_game", "menu")
    builder.add_edge("start_word_game", "start_word_game")
    builder.add_edge("start_word_game", "menu")
    builder.set_finish_point("menu")
    return builder.compile()

# Main function
def main():
    if "game_state" not in st.session_state:
        st.session_state.game_state = initialize_state()

    game_graph = create_game_graph()

    # Process the game flow
    for updated_state in game_graph.stream(st.session_state.game_state):
        st.session_state.game_state = updated_state
        # We ensure the state only returns to "menu" once we are done with the game
        if updated_state.get("_next") == "menu":
            break

if __name__ == "__main__":
    main()
