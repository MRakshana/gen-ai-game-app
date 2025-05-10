def number_game_agent(state: GameState) -> GameState:
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)
    session_id = st.session_state.get('session_id', 0)
    game_count = state["number_game_count"]
    
    with col1:
        # Ensure each button has a unique key by incorporating session_id and game_count
        button_key = f"yes_{session_id}_{game_count}_{min_val}_{max_val}"
        if st.button(f"Yes_{session_id}_{game_count}", key=button_key):
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
        # Ensure each button has a unique key by incorporating session_id and game_count
        button_key = f"no_{session_id}_{game_count}_{min_val}_{max_val}"
        if st.button(f"No_{session_id}_{game_count}", key=button_key):
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
