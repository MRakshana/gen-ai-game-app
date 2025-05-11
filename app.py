from typing import Annotated, TypedDict
import operator
from langgraph.graph import StateGraph, END

# 1. Define your state schema
class GameState(TypedDict):
    _next: Annotated[list[str], operator.mul]  # allow multiple transitions
    value: int

# 2. Define your node handlers
def start_node(state: GameState) -> GameState:
    print("Start node executing.")
    # Decide to go to two other nodes
    return {
        "_next": ["check_even", "check_positive"],
        "value": state["value"]
    }

def check_even(state: GameState) -> GameState:
    if state["value"] % 2 == 0:
        print("Even number.")
    else:
        print("Odd number.")
    return {"_next": END, "value": state["value"]}

def check_positive(state: GameState) -> GameState:
    if state["value"] > 0:
        print("Positive number.")
    else:
        print("Non-positive number.")
    return {"_next": END, "value": state["value"]}

# 3. Define the graph
builder = StateGraph(GameState)

builder.add_node("start", start_node)
builder.add_node("check_even", check_even)
builder.add_node("check_positive", check_positive)

builder.set_entry_point("start")
builder.add_edge("check_even", END)
builder.add_edge("check_positive", END)

graph = builder.compile()

# 4. Run the graph
initial_state = {"_next": ["start"], "value": 5}
graph.invoke(initial_state)
