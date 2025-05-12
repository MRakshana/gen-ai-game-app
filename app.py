import streamlit as st
from langgraph.graph import StateGraph
from typing import TypedDict, Literal, Optional

# Game state structure
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
    st.write(f"Is your number {state['current_guess']}?")
    feedback = st.radio(
        "Choose feedback:",
        ["greater", "less", "correct"],
        key=f"feedback_{state['current_guess']}"
    )
    return {**state, "feedback": feedback}

# Node 3: Update min/max bounds based on feedback
def process_feedback(state: NumberGameState) -> NumberGameState:
    guess = state["current_guess"]
    if state["feedback"] == "greater":
        state["min_val"] = guess + 1
    elif state["feedback"] == "less":
        state["max_val"] = guess - 1
    return state

# Node 4: Compute next guess or finish
def check_win(state: NumberGameState) -> NumberGameState:
    if state["feedback"] == "correct":
        state["done"] = True  # Mark game as done when feedback is 'correct'
    else:
        state["current_guess"] = (state["min_val"] + state["max_val"]) // 2
    return state

# Node 5: End game
def end_game(state: NumberGameState) -> NumberGameState:
    if state["done"]:
        st.success(f"🎉 I guessed your number: {state['current_guess']}!")
    return state

# Build LangGraph with recursion limit
def build_number_game_graph():
    graph = StateGraph(NumberGameState, recursion_limit=50)  # Increase recursion limit

    graph.add_node("initialize", initialize_game)
    graph.add_node("show_guess", show_guess)
    graph.add_node("process_feedback", process_feedback)
    graph.add_node("check_win", check_win)
    graph.add_node("end", end_game)

    graph.set_entry_point("initialize")
    graph.add_edge("initialize", "show_guess")
    graph.add_edge("show_guess", "process_feedback")
    graph.add_edge("process_feedback", "check_win")
    graph.add_conditional_edges("check_win", lambda state: "end" if state["done"] else "show_guess")
    graph.set_finish_point("end")

    return graph.compile()

# Streamlit UI
st.title("🎮 Number Guessing Game (LangGraph Powered)")

if "state" not in st.session_state:
    st.session_state["state"] = None
    st.session_state["runner"] = build_number_game_graph()

if st.button("Start Game"):
    st.session_state["state"] = st.session_state["runner"].invoke({})

if st.session_state["state"]:
    st.session_state["state"] = st.session_state["runner"].invoke(st.session_state["state"])

import graphviz

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
    dot.edge("check_win", "show_guess", label="not done")
    dot.edge("check_win", "end", label="done")

    return dot

with st.expander("🧠 View LangGraph Execution Flow"):
    st.graphviz_chart(visualize_graph())
