from langgraph.graph import StateGraph, END

def build_game_graph():
    builder = StateGraph()

    builder.add_node("start_game", start_game_node)
    builder.add_node("play_turn", play_turn_node)
    builder.add_node("check_end", check_end_node)

    builder.set_entry_point("start_game")
    builder.add_edge("start_game", "play_turn")
    builder.add_edge("play_turn", "check_end")

    builder.add_conditional_edges(
        "check_end", lambda state: END if state.get("end", False) else "play_turn"
    )

    return builder.compile()
