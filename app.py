from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1. Define the state schema
class GameState(TypedDict):
    _next: list[str]  # No need for Multiple annotation
    value: int

# 2. Define your node functions
def start_node(state: GameState) -> GameState:
    print("\n[Start Node]")
    value = state["value"]
    next_steps = []

    if value % 2 == 0:
        next_steps.append("check_even")
    else:
        next_steps.append("check_odd")

    if value > 0:
        next_steps.append("check_positive")
    else:
        next_steps.append("check_non_positive")

    return {"_next": next_steps, "value": value}


def check_even(state: GameState) -> GameState:
    print("✔️ It's even!")
    return {"_next": [END], "value": state["value"]}

def check_odd(state: GameState) -> GameState:
    print("✔️ It's odd!")
    return {"_next": [END], "value": state["value"]}

def check_positive(state: GameState) -> GameState:
    print("✔️ It's positive!")
    return {"_next": [END], "value": state["value"]}

def check_non_positive(state: GameState) -> GameState:
    print("✔️ It's zero or negative!")
    return {"_next": [END], "value": state["value"]}

# 3. Create the graph
builder = StateGraph(GameState)

builder.add_node("start", start_node)
builder.add_node("check_even", check_even)
builder.add_node("check_odd", check_odd)
builder.add_node("check_positive", check_positive)
builder.add_node("check_non_positive", check_non_positive)

builder.set_entry_point("start")
builder.add_edge("check_even", END)
builder.add_edge("check_odd", END)
builder.add_edge("check_positive", END)
builder.add_edge("check_non_positive", END)

graph = builder.compile()

# 4. Invoke the graph
print("Running LangGraph...\n")
initial_state = {"_next": ["start"], "value": 3}  # Try different numbers!
graph.invoke(initial_state)
