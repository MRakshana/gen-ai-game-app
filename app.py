import streamlit as st
from graph import build_graph

st.set_page_config(page_title="Gen AI Game App")
st.title("🎮 Gen AI Game App")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
    st.session_state.state = {
        "correct_number": "",
        "guess": "",
        "message": "",
        "end": False,
    }
    st.session_state.state = st.session_state.graph.invoke(st.session_state.state)

st.write(st.session_state.state["message"])

if not st.session_state.state.get("end", False):
    guess = st.text_input("Enter your guess:")
    if st.button("Submit Guess"):
        st.session_state.state["guess"] = guess
        st.session_state.state = st.session_state.graph.invoke(st.session_state.state)
        st.rerun()
else:
    st.success("Game over!")
