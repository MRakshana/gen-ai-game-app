from uuid import uuid4  # Make sure this is at the top of your script

def number_game_agent(state: GameState) -> GameState:
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes", key=f"number_game_yes_{uuid4()}"):
            state["number_guess_min"] = mid + 1
            if state["number_guess_min"] == state["number_guess_max"]:
                st.write(f"Your number is {state['number_guess_min']}! I guessed it!")
                state["number_game_count"] += 1
                state["session_games"].append("number")
                state["number_guess_min"] = 1
                state["number_guess_max"] = 50
                state["_next"] = "menu"
            else:
                state["_next"] = "start_number_game"

    with col2:
        if st.button("No", key=f"number_game_no_{uuid4()}"):
            state["number_guess_max"] = mid
            if state["number_guess_min"] == state["number_guess_max"]:
                st.write(f"Your number is {state['number_guess_min']}! I guessed it!")
                state["number_game_count"] += 1
                state["session_games"].append("number")
                state["number_guess_min"] = 1
                state["number_guess_max"] = 50
                state["_next"] = "menu"
            else:
                state["_next"] = "start_number_game"

    return state
