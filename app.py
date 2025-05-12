import streamlit as st
from langgraph.graph import StateGraph
from typing import TypedDict, Literal, Optional

# --- Game State Definition ---
class NumberGameState(TypedDict):
    min_val: int
    max_val: int
    current_guess: int
    feedback: Optional[Literal["greater", "less", "correct"]]
    done: bool

# --- LangGraph Nodes ---
def initialize_game(_: NumberGameState) -> NumberGameState:
    min_val, max_val = 1, 50
    guess = (min_val + max_val) // 2
    return {"min_val": min_val, "max_val": max_val, "current_guess": guess, "feedback": None, "done": False}

def show_guess(state: NumberGameState) -> NumberGameState:
    # This node does nothing now; feedback is handled in Streamlit UI
    return state

def process_feedback(state: NumberGameState) -> NumberGameState:
    guess = state["current_guess"]
    if state["feedback"] == "greater":
        state["min_val"] = guess + 1
    elif state["feedback"] == "less":
        state["max_val"] = guess - 1
    return state

def check_win(state: NumberGameState) -> NumberGameState:
    if state["feedback"] == "correct":
        state["done"] = True
    else:
        state["current_guess"] = (state["min_val"] + state["max_val"]) // 2
    return state

def end_game(state: NumberGameState) -> NumberGameState:
    return state

# --- LangGraph Builder ---
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
    graph.add_conditional_edges("check_win", lambda s: "end" if s["done"] else "show_guess")
    graph.set_finish_point("end")

    return graph.compile()

# --- Streamlit UI ---
st.title("🎮 Number Guessing Game (LangGraph Powered)")

if "runner" not in st.session_state:
    st.session_state.runner = build_number_game_graph()

if "state" not in st.session_state:
    st.session_state.state = None

if st.button("Start Game"):
    st.session_state.state = st.session_state.runner.invoke({})

# Game Loop (UI + LangGraph step)
if st.session_state.state:
    state = st.session_state.state

    if state["done"]:
        st.success(f"🎉 I guessed your number: {state['current_guess']}!")
        if st.button("Play Again"):
            st.session_state.state = None
    else:
        st.write(f"Is your number {state['current_guess']}?")

        # Generate a unique key by including the guess and session id
        unique_key = f"feedback_{state['current_guess']}_{st.session_state.get('game_id', 0)}"
        
        feedback = st.radio("Choose feedback:", ["greater", "less", "correct"], key=unique_key)
        
        if st.button("Submit Response"):
            state["feedback"] = feedback
            st.session_state.state = st.session_state.runner.invoke(state)

# Optional: Show graph
import graphviz

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
