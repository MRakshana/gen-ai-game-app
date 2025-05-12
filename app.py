import random
import time
import streamlit as st
from typing import Annotated, List, Literal, TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import AnyMessage

# Define your state
class GameState(TypedDict):
    game_type: Literal["number", "word"]
    step: str
    messages: Annotated[List[AnyMessage], "merge"]

# Number guessing logic
def number_game_agent(state: GameState) -> GameState:
    messages = state["messages"]
    guesses = [m["content"] for m in messages if m["type"] == "user"]

    if not guesses:
        # First guess
        guess = random.randint(1, 50)
    else:
        # Process the last user response and guess
        last_response = guesses[-1].lower()
        prev_guess = int([m["content"] for m in messages if m["type"] == "ai"][-1].split()[-1].replace("?", ""))

        if last_response == "greater":
            guess = min(50, prev_guess + 1)
        elif last_response == "less":
            guess = max(1, prev_guess - 1)
        elif last_response == "correct":
            # End game when correct answer is given
            st.success(f"🎉 Congrats! I guessed your number {prev_guess}!")
            st.session_state["game_counter"] += 1
            st.session_state["state"] = "main"
            return {"game_type": "number", "step": "done", "messages": []}
        else:
            # Handle invalid response
            st.warning("Please provide a valid response.")
            return state

    # Ask the user if the guess is correct
    st.write(f"Is your number {guess}?")
    response = st.radio(
        "Select if the guess is correct",
        ["greater", "less", "correct"],
        key=f"guess_{guess}_{len(messages)}"
    )

    # Append the AI's guess and user's response to messages
    messages.append({"type": "ai", "content": f"Is your number {guess}?"})
    messages.append({"type": "user", "content": response})

    return {
        "game_type": "number",
        "step": "number_game",
        "messages": messages
    }

# Word clue logic
def word_game_agent(state: GameState) -> GameState:
    words = ["apple", "chair", "elephant", "guitar", "rocket", "pencil", "pizza", "tiger"]
    if "word_choice" not in st.session_state:
        st.session_state["word_choice"] = random.choice(words)
        st.session_state["word_guesses"] = []

    st.write("Choose a word from the following list:")
    st.json({i: w for i, w in enumerate(words)})

    question = st.text_input("Ask a yes/no question to guess the word:")
    if question:
        answer = "Maybe"
        target_word = st.session_state["word_choice"]
        if any(word in target_word for word in question.lower().split()):
            answer = "Yes"
        elif random.random() > 0.5:
            answer = "No"
        st.session_state["word_guesses"].append((question, answer))
        for q, a in st.session_state["word_guesses"]:
            st.radio(q, ["Yes", "No", "Maybe"], index=["Yes", "No", "Maybe"].index(a))

    return {
        "game_type": "word",
        "step": "word_game",
        "messages": [{"type": "user", "content": question}] if question else []
    }

def build_game_graph():
    builder = StateGraph(GameState)
    builder.add_node("number_game", number_game_agent)
    builder.add_node("word_game", word_game_agent)

    builder.set_entry_point("number_game")
    builder.set_finish_point("word_game")

    return builder.compile()

# Streamlit UI
st.title("Welcome to the Game Hub")

if "game_counter" not in st.session_state:
    st.session_state["game_counter"] = 0

if "state" not in st.session_state:
    st.session_state["state"] = "main"

if "messages" not in st.session_state:
    st.session_state["messages"] = []

game_type = st.radio("Choose a game mode", ["Number Game", "Word Clue Guesser"])

if st.button(f"Start {game_type}"):
    st.session_state["state"] = "number" if "Number" in game_type else "word"
    st.session_state["messages"] = []

if st.session_state["state"] == "number":
    st.write("Welcome to the Number Game!")
    st.write("Think of a number between 1 and 50, and I'll guess it.")

    state = {
        "game_type": "number",
        "step": "number_game",
        "messages": st.session_state.get("messages", [])
    }

    result = number_game_agent(state)

    if result and "messages" in result:
        st.session_state["messages"] = result["messages"]

elif st.session_state["state"] == "word":
    st.write("Welcome to the Word Clue Guesser!")
    word_game_agent({"game_type": "word", "step": "start", "messages": []})

elif st.session_state["state"] == "main":
    st.write(f"Number Game counter: {st.session_state['game_counter']}")
    st.write("Returning to the main menu...")
    time.sleep(2)
    st.session_state["state"] = ""
