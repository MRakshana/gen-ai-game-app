import streamlit as st

def visualize_structure_enhanced():
    st.subheader("Game Flow Visualization")

    dot_str = """
    digraph {
        rankdir=LR;
        node [fontname="Arial", shape=box, style=filled, color=lightgray];

        Start [shape=ellipse, fillcolor=lightgreen];
        End [shape=ellipse, fillcolor=lightgreen];
        "Choose Game" [shape=diamond, fillcolor=lightblue];
        "Play Again?" [shape=diamond, fillcolor=lightblue];

        Start -> "Choose Game";

        "Choose Game" -> "Start Number Game" [label="Number"];
        "Choose Game" -> "Start Word Game" [label="Word"];

        "Start Number Game" -> "Number Guessing";
        "Number Guessing" -> "Number Guessing" [label="Wrong Guess", style=dashed];
        "Number Guessing" -> "Number Game Over";

        "Start Word Game" -> "Word Guessing";
        "Word Guessing" -> "Word Guessing" [label="Wrong Guess", style=dashed];
        "Word Guessing" -> "Word Game Over";

        "Number Game Over" -> "Play Again?";
        "Word Game Over" -> "Play Again?";

        "Play Again?" -> "Choose Game" [label="Yes"];
        "Play Again?" -> End [label="No"];
    }
    """

    st.graphviz_chart(dot_str)
