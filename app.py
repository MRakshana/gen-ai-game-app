# Inside app.py
import streamlit as st
from langgraph.graph import StateGraph
from typing import TypedDict, Literal, Optional
import graphviz

# Game state structure
class NumberGameState(TypedDict):
    min_val: int
    max_val: int
    current_guess: int
    feedback: Optional[Literal["greater", "less", "correct"]]
    done: bool

# Game logic nodes
def initialize_game(_: NumberGameState) -> NumberGameState:
    min_val, max_val = 1, 50
    guess = (min_val + max_val) // 2
    return {"min_val": min_val, "max_val": max_val, "current_guess": guess, "feedback": None, "done": False}

def show_guess(state: NumberGameState) -> NumberGameState:
    st.write(f"Is your number {state['current_guess']}?")
    feedback = st.radio("Your feedback:", ["greater", "less", "correct"], key=f"feedback_{state['current_guess']}")
    return {**state, "feedback": feedback}

def process_feedback(state: NumberGameState) -> NumberGameState:
    if state["feedback"] == "greater":
        state["min_val"] = state["current_guess"] + 1
    elif state["feedback"] == "less":
        state["max_val"] = state["current_guess"] - 1
    return state

def check_win(state: NumberGameState) -> NumberGameState:
    if state["feedback"] == "correct":
        state["done"] = True
    else:
        state["current_guess"] = (state["min_val"] + state["max_val"]) // 2
    return state

def end_game(state: NumberGameState) -> NumberGameState:
    st.success(f"🎉 I guessed your number: {state['current_guess']}!")
    return state

# Build the graph
def build_number_game_graph():
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
    graph.add_conditional_edges("check_win", lambda state: "end" if state["done"] else "show_guess")
    graph.set_finish_point("end")

    return graph.compile()

# ---- Streamlit App UI ----
st.title("🎮 Number Guessing Game (LangGraph)")

if "runner" not in st.session_state:
    st.session_state.runner = build_number_game_graph()
    st.session_state.generator = None
    st.session_state.state = None

if st.button("Start New Game"):
    st.session_state.generator = st.session_state.runner.stream({})
    st.session_state.state = None

# Move to the next step on each run
if st.session_state.generator:
    try:
        for event in st.session_state.generator:
            st.session_state.state = event
            break  # Only one step per interaction
    except StopIteration:
        st.session_state.generator = None

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

with st.expander("🧠 Execution Graph"):
    st.graphviz_chart(visualize_graph())

