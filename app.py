import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict

# ----------------------------
# Define GameState TypedDict
# ----------------------------
class GameState(TypedDict):
    _next: str
    number_guess_min: int
    number_guess_max: int
    number_game_count: int
    word_game_count: int
    session_games: list[str]

# ----------------------------
# Initialize the game state
# ----------------------------
def initialize_state() -> GameState:
    return GameState(
        _next="menu",
        number_guess_min=1,
        number_guess_max=50,
        number_game_count=0,
        word_game_count=0,
        session_games=[],
    )

# ----------------------------
# Menu Agent
# ----------------------------
def menu(state: GameState) -> GameState:
    st.title("🧠 Gen AI Game App")
    st.subheader("Choose a game")
    col1, col2 = st.columns(2)

    if col1.button("Play Number Guessing Game"):
        state["_next"] = "start_number_game"
    elif col2.button("Play Word Clue Game"):
        state["_next"] = "start_word_game"
    else:
        state["_next"] = "menu"

    return state

# ----------------------------
# Number Guessing Game Agent
# ----------------------------
def number_game_agent(state: GameState) -> GameState:
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    if min_val >= max_val:
        st.success(f"🎯 Your number is {min_val}! I guessed it!")
        state["number_game_count"] += 1
        state["session_games"].append("number")
        state["number_guess_min"] = 1
        state["number_guess_max"] = 50
        state["_next"] = "menu"
        return state

    if "last_guess" not in st.session_state:
        st.session_state.last_guess = None

    st.write("Number Game Agent")
    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)

    if col1.button("Yes"):
        st.session_state.last_guess = "yes"
    elif col2.button("No"):
        st.session_state.last_guess = "no"

    if st.session_state.last_guess == "yes":
        state["number_guess_min"] = mid + 1
        st.session_state.last_guess = None
    elif st.session_state.last_guess == "no":
        state["number_guess_max"] = mid
        st.session_state.last_guess = None
    else:
        state["_next"] = "start_number_game"
        return state

    state["_next"] = "start_number_game"
    return state

# ----------------------------
# Word Clue Guessing Game Agent
# ----------------------------
def word_game_agent(state: GameState) -> GameState:
    st.write("Word Game Agent")
    st.write("Clue: It's a large animal with a trunk.")
    answer = st.text_input("Your Guess:", key="word_game_input")

    if answer.lower() == "elephant":
        st.success("Correct! 🎉")
        state["word_game_count"] += 1
        state["session_games"].append("word")
        state["_next"] = "menu"
    else:
        st.warning("Try again!")
        state["_next"] = "start_word_game"

    return state

# ----------------------------
# Build the Game Graph
# ----------------------------
def create_game_graph():
    builder = StateGraph(GameState)
    builder.add_node("menu", menu)
    builder.add_node("start_number_game", number_game_agent)
    builder.add_node("start_word_game", word_game_agent)

    builder.set_entry_point("menu")
    builder.set_finish_point("menu")

    builder.add_edge("menu", "start_number_game")
    builder.add_edge("menu", "start_word_game")
    builder.add_edge("start_number_game", "start_number_game")
    builder.add_edge("start_number_game", "menu")
    builder.add_edge("start_word_game", "start_word_game")
    builder.add_edge("start_word_game", "menu")

    return builder.compile()

# ----------------------------
# Main Application
# ----------------------------
def main():
    if "game_state" not in st.session_state:
        st.session_state.game_state = initialize_state()

    game_graph = create_game_graph()

    for updated_state in game_graph.stream(st.session_state.game_state):
        if "_next" in updated_state and updated_state["_next"] == "menu":
        st.session_state.game_state = updated_state
        break
    st.session_state.game_state = updated_state


if __name__ == "__main__":
    main()
