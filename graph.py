# graph.py
# graph.py

from langgraph.graph import END, StateGraph
from typing import TypedDict, Optional

class GameState(TypedDict):
    guess: Optional[str]
    correct_number: str
    message: Optional[str]
    end: bool

# Define nodes
def start_game(state: GameState) -> GameState:
    state["correct_number"] = "5"  # fixed for simplicity
    state["message"] = "Guess a number between 1 and 10:"
    state["end"] = False  # Ensure the game doesn't end at the start
    return state

def check_guess(state: GameState) -> GameState:
    if state["guess"] == state["correct_number"]:
        state["message"] = "🎉 Correct! You win!"
        state["end"] = True
    else:
        state["message"] = f"❌ Incorrect. Try again!"
        state["end"] = False
    return state

# Build graph
def build_graph():
    builder = StateGraph(GameState)

    builder.add_node("start", start_game)
    builder.add_node("check", check_guess)

    builder.set_entry_point("start")

    builder.add_edge("start", "check")  # Connect start to check
    builder.add_edge("check", "check", condition=lambda s: not s["end"])  # Continue checking if game not ended
    builder.add_edge("check", END, condition=lambda s: s["end"])  # End game if correct number guessed

    return builder.compile()
