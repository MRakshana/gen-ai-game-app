import streamlit as st
from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1. Define the state schema
class GameState(TypedDict):
    _next: list[str]  # List of nodes to transition to
    value: int

# 2. Define your node functions with added debug prints
def start_node(state: GameState) -> GameState:
    st.write("\n[Start Node]")
    value = state["value"]
    next_steps = []

    # Determine next steps based on the value
    if value % 2 == 0:
        next_steps.append("check_even")
    else:
        next_steps.append("check_odd")

    if value > 0:
        next_steps.append("check_positive")
    else:
        next_steps.append("check_non_positive")

    st.write(f"Next steps: {next_steps}")
    return {"_next": next_steps, "value": value}


def check_even(state: GameState) -> GameState:
    st.write(f"✔️ It's even! Current value: {state['value']}")
    return {"_next": [END], "value": state["value"]}

def check_odd(state: GameState) -> GameState:
    st.write(f"✔️ It's odd! Current value: {state['value']}")
    return {"_next": [END], "value": state["value"]}

def check_positive(state: GameState) -> GameState:
    st.write(f"✔️ It's positive! Current value: {state['value']}")
    return {"_next": [END], "value": state["value"]}

def check_non_positive(state: GameState) -> GameState:
    st.write(f"✔️ It's zero or negative! Current value: {state['value']}")
    return {"_next": [END], "value": state["value"]}

# 3. Create the graph
builder = StateGraph(GameState)

# Add nodes to the graph
builder.add_node("start", start_node)
builder.add_node("check_even", check_even)
builder.add_node("check_odd", check_odd)
builder.add_node("check_positive", check_positive)
builder.add_node("check_non_positive", check_non_positive)

# Set the entry point
builder.set_entry_point("start")

# Define edges to terminate the graph
builder.add_edge("check_even", END)
builder.add_edge("check_odd", END)
builder.add_edge("check_positive", END)
builder.add_edge("check_non_positive", END)

# Compile the graph
graph = builder.compile()

# 4. Streamlit UI
st.title("LangGraph Game")
st.write("This is a simple number game where we check if a number is odd, even, positive, or non-positive.")

# Add input to the Streamlit app
number = st.number_input("Enter a number", value=3)

# Initial state for the graph
initial_state = {"_next": ["start"], "value": number}

# Button to invoke the graph
if st.button("Run Game"):
    st.write("Running LangGraph...")
    graph.invoke(initial_state)
