import streamlit as st
from langgraph.graph import StateGraph
from typing import TypedDict, Literal, Optional
import graphviz

# Define game state structure
class NumberGameState(TypedDict):
    min_val: int
    max_val: int
    current_guess: int
    feedback: Optional[Literal["greater", "less", "correct"]]
    done: bool

# Node 1: Initialize the game
def initialize_game(_: NumberGameState) -> NumberGameState:
    min_val, max_val = 1, 50
    guess = (min_val + max_val) // 2
    return {"min_val": min_val, "max_val": max_val, "current_guess": guess, "feedback": None, "done": False}

# Node 2: Display guess and take feedback
def show_guess(state: NumberGameState) -> NumberGameState:
    if state["done"]:
        return state
    st.write(f"Is your number {state['current_guess']}?")
    feedback = st.radio(
        "Choose feedback:",
        ["greater", "less", "correct"],
        key=f"feedback_{state['current_guess']}"
    )
    if st.button("Submit Feedback"):
        state["feedback"] = feedback
        st.session_state["advance"] = True  # trigger next step
    return state

# Node 3: Update guess bounds
def process_feedback(state: NumberGameState) -> NumberGameState:
    if state["feedback"] == "greater":
        state["min_val"] = state["current_guess"] + 1
    elif state["feedback"] == "less":
        state["max_val"] = state["current_guess"] - 1
    return state

# Node 4: Check for win or inconsistency
def check_win(state: NumberGameState) -> NumberGameState:
    if state["feedback"] == "correct":
        state["done"] = True
    elif state["min_val"] > state["max_val"]:
        st.error("Inconsistent feedback. Ending game.")
        state["done"] = True
    else:
        state["current_guess"] = (state["min_val"] + state["max_val"]) // 2
    return state

# Node 5: Final node
def end_game(state: NumberGameState) -> NumberGameState:
    if state["done"]:
        st.success(f"🎉 I guessed your number: {state['current_guess']}!")
    return state

# Define LangGraph
def build_number_game_graph():
    graph = StateGraph(NumberGameState)

    graph.add_node("initialize", initialize_game)
    graph.add_node("show_guess", show_guess)
    graph.add_node("process_feedback", process_feedback)
    graph.add_node("check_win", check_win)
    graph.add_node("end", end_game)

    graph.set_entry_point("initialize")
    graph.set_finish_point("end")

    graph.add_edge("initialize", "show_guess")
    graph.add_edge("show_guess", "process_feedback")
    graph.add_edge("process_feedback", "check_win")
    graph.add_conditional_edges("check_win", lambda state: "end" if state["done"] else "show_guess")

    return graph.compile()

# Streamlit app
st.title("🤖 Number Guessing Game (LangGraph)")

if "runner" not in st.session_state:
    st.session_state.runner = build_number_game_graph()
    st.session_state.iterator = None
    st.session_state.current_state = None
    st.session_state.advance = False

# Start new game
if st.button("🔁 Start New Game"):
    st.session_state.iterator = st.session_state.runner.stream({})
    st.session_state.current_state = next(st.session_state.iterator)
    st.session_state.advance = False

# Run one step at a time
if st.session_state.current_state:
    st.session_state.current_state = st.session_state.iterator.send(st.session_state.current_state)
    if st.session_state.current_state["done"]:
        st.session_state.iterator = None  # Stop further steps

# Proceed to next step only when user submitted feedback
if st.session_state.advance:
    st.session_state.advance = False
    st.rerun()

# Visualize LangGraph
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

