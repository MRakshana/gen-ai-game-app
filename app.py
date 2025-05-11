import gradio as gr
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated

# Define GameState
class GameState(TypedDict):
    _next: Annotated[str, "output"]
    number_guess_min: int
    number_guess_max: int
    number_game_count: int
    word_game_count: int
    session_games: list[str]

# Initialize game state
def initialize_state() -> GameState:
    return {
        "_next": "menu",
        "number_guess_min": 1,
        "number_guess_max": 50,
        "number_game_count": 0,
        "word_game_count": 0,
        "session_games": [],
    }

# Menu agent
def menu(state: GameState) -> GameState:
    return state  # No-op; Gradio handles button triggers externally

# Number guessing logic
def number_game_agent(state: GameState, user_input: str = None) -> GameState:
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    if user_input == "yes":
        state["number_guess_min"] = mid + 1
    elif user_input == "no":
        state["number_guess_max"] = mid

    if state["number_guess_min"] >= state["number_guess_max"]:
        state["number_game_count"] += 1
        state["session_games"].append("number")
        state["_next"] = "menu"
        state["number_guess_min"] = 1
        state["number_guess_max"] = 50
    else:
        state["_next"] = "start_number_game"

    return state

# Word guessing logic
def word_game_agent(state: GameState, guess: str = "") -> GameState:
    if guess.lower() == "elephant":
        state["word_game_count"] += 1
        state["session_games"].append("word")
        state["_next"] = "menu"
    else:
        state["_next"] = "start_word_game"
    return state

# Game flow graph
def create_game_graph():
    builder = StateGraph(GameState)
    builder.add_node("menu", menu)
    builder.add_node("start_number_game", number_game_agent)
    builder.add_node("start_word_game", word_game_agent)
    builder.set_entry_point("menu")
    builder.set_finish_point("menu")
    builder.add_edge("menu", "start_number_game")
    builder.add_edge("menu", "start_word_game")
    builder.add_edge("start_number_game", "menu")
    builder.add_edge("start_number_game", "start_number_game")
    builder.add_edge("start_word_game", "menu")
    builder.add_edge("start_word_game", "start_word_game")
    return builder.compile()

# Gradio UI
state = initialize_state()
graph = create_game_graph()

def game_interface(choice=None, response=None):
    global state
    if state["_next"] == "menu":
        if choice == "Number":
            state["_next"] = "start_number_game"
        elif choice == "Word":
            state["_next"] = "start_word_game"

    for updated_state in graph.stream(state):
        state = updated_state
        if updated_state["_next"] == "menu":
            break

    mid = (state["number_guess_min"] + state["number_guess_max"]) // 2
    if state["_next"] == "start_number_game":
        return f"Is your number greater than {mid}?", ["yes", "no"]
    elif state["_next"] == "start_word_game":
        return "Clue: It's a large animal with a trunk. Guess the word:", ["elephant"]
    else:
        return "Choose a game to play:", ["Number", "Word"]

iface = gr.Interface(
    fn=game_interface,
    inputs=[gr.Radio(["Number", "Word", "yes", "no", "elephant"], label="Input")],
    outputs=[gr.Text(), gr.Label()],
    title="GenAI Game App",
)

iface.launch()
