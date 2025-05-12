# graph.py

from langgraph.graph import END, StateGraph
from typing import TypedDict, Optional

# Define the shared game state
class GameState(TypedDict):
    guess: Optional[str]
    correct_number: str
    message: Optional[str]
    end: bool

# Node: start the game
def start_game(state: GameState) -> GameState:
    state["correct_number"] = "5"  # You can randomize this if needed
    state["message"] = "Guess a number between 1 and 10:"
    state["end"] = False
    return state

# Node: check the guess
def check_guess(state: GameState) -> GameState:
    if state["guess"] == state["correct_number"]:
        state["message"] = "🎉 Correct! You win!"
        state["end"] = True
    else:
        state["message"] = "❌ Incorrect. Try again!"
        state["end"] = False
    return state

# Function to build the LangGraph
def build_graph():
    builder = StateGraph(GameState)

    builder.add_node("start", start_game)
    builder.add_node("check", check_guess)

    builder.set_entry_point("start")

    builder.add_edge("start", "check")
    builder.add_conditional_edges(
        "check",
        condition=lambda s: END if s["end"] else "check"
    )

    return builder.compile()
