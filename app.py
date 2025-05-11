from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END, Multiple

# 1. Define state schema
class GameState(TypedDict):
    _next: Annotated[list[str], Multiple()]  # <-- FIXED HERE
    value: int

# 2. Node functions
def start_node(state: GameState) -> GameState:
    print("Start node executing.")
    return {
        "_next": ["check_even", "check_positive"],  # Multiple transitions
        "value": state["value"]
    }

def check_even(state: GameState) -> GameState:
    print("Even" if state["value"] % 2 == 0 else "Odd")
    return {"_next": [END], "value": state["value"]}

def check_positive(state: GameState) -> GameState:
    print("Positive" if state["value"] > 0 else "Non-positive")
    return {"_next": [END], "value": state["value"]}

# 3. Graph construction
builder = StateGraph(GameState)
builder.add_node("start", start_node)
builder.add_node("check_even", check_even)
builder.add_node("check_positive", check_positive)

builder.set_entry_point("start")
builder.add_edge("check_even", END)
builder.add_edge("check_positive", END)

graph = builder.compile()

# 4. Run
initial_state = {"_next": ["start"], "value": 5}
graph.invoke(initial_state)
