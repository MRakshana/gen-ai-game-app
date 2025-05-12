import streamlit as st
from langgraph.graph import StateGraph
from typing import TypedDict, Literal, Optional
import graphviz

# Define game state
class NumberGameState(TypedDict):
    min_val: int
    max_val: int
    current_guess: int
    feedback: Optional[Literal["greater", "less", "correct"]]
    done: bool

# Node 1: Initialize game
def initialize_game(_: NumberGameState) -> NumberGameState:
    min_val, max_val = 1, 50
    guess = (min_val + max_val) // 2
    return {"min_val": min_val, "max_val": max_val, "current_guess": guess, "feedback": None, "done": False}

# Node 2: Show guess and get user feedback
def show_guess(state: NumberGameState) -> NumberGameState:
    if state["done"]:
        return state
    st.write(f"Is your number {state['current_guess']}?")
    feedback = st.radio(
        "Choose feedback:",
        ["greater", "less", "correct"],
        key=f"feedback_{state['current_guess']}"
    )
    return {**state, "feedback": feedback}

# Node 3: Process feedback
def process_feedback(state: NumberGameState) -> NumberGameState:
    if state["feedback"] == "greater":
        state["min_val"] = state["current_guess"] + 1
    elif state["feedback"] == "less":
        state["max_val"] = state["current_guess"] - 1
    return state

# Node 4: Check win condition
def check_win(state: NumberGameState) -> NumberGameState:
    if state["feedback"] == "correct":
        state["done"] = True
    else:
        state["current_guess"] = (state["min_val"] + state["max_val"]) // 2
    return state

# Node 5: End game
def end_game(state: NumberGameState) -> NumberGameState:
    if state["done"]:
        st.success(f"\U0001F389 I guessed your number: {state['current_guess']}!")
    return state

# Build LangGraph
def build_graph():
    graph = StateGraph(NumberGameState)
    graph.add_node("initialize", initialize_game)
    graph.add_node("show_guess", show_guess)
    graph.add_node("process_feedback", process_feedback)
    graph.add_node("check_win", check_win)
    graph.add_node("end", end_game)

    graph.set_entry_point("initialize")
    graph.add_edge("initialize", "show_guess")
    graph.add_edge("show_guess", "process_feedback")
    graph.add_edge("process_feedback", "check_win")
    graph.add_conditional_edges("check_win", lambda s: "end" if s["done"] else "show_guess")
    graph.set_finish_point("end")

    return graph.compile()

# Visualize the graph
def visualize_graph():
    dot = graphviz.Digraph()
    dot.node("initialize")
    dot.node("show_guess")
    dot.node("process_feedback")
    dot.node("check_win")
    dot.node("end")

    dot.edge("initialize", "show_guess")
    dot.edge("show_guess", "process_feedback")
    dot.edge("process_feedback", "check_win")
    dot.edge("check_win", "end", label="done")
    dot.edge("check_win", "show_guess", label="not done")

    return dot

# Streamlit UI
st.title("\U0001F3AE Number Guessing Game (LangGraph)")

if "state" not in st.session_state:
    st.session_state.state = None
    st.session_state.runner = build_graph()
    st.session_state.current_node = "initialize"

if st.button("Next Step"):
    if st.session_state.state is None:
        st.session_state.state = {}
    st.session_state.state, next_node = st.session_state.runner.invoke_step(
        st.session_state.current_node, st.session_state.state
    )
    if next_node:
        st.session_state.current_node = next_node

if st.session_state.state:
    st.json(st.session_state.state)

with st.expander("\U0001F9E0 View Graph"):
    st.graphviz_chart(visualize_graph())
