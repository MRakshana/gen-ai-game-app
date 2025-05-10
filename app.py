def number_game_agent(state: GameState) -> GameState:
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    st.write(f"Is your number greater than {mid}?")
    col1, col2 = st.columns(2)

    # Ensure keys are always unique using session + count + min/max
    session_id = st.session_state.get('session_id', 0)
    game_id = state["number_game_count"]
    key_suffix = f"{session_id}_{game_id}_{min_val}_{max_val}"

    # Use session state to capture button clicks only once
    if f"number_response_{key_suffix}" not in st.session_state:
        with col1:
            if st.button("Yes", key=f"number_game_yes_{key_suffix}"):
                st.session_state[f"number_response_{key_suffix}"] = "yes"
        with col2:
            if st.button("No", key=f"number_game_no_{key_suffix}"):
                st.session_state[f"number_response_{key_suffix}"] = "no"

    if f"number_response_{key_suffix}" in st.session_state:
        answer = st.session_state[f"number_response_{key_suffix}"]
        if answer == "yes":
            state["number_guess_min"] = mid + 1
        else:
            state["number_guess_max"] = mid

        if state["number_guess_min"] == state["number_guess_max"]:
            st.success(f"Your number is {state['number_guess_min']}! I guessed it!")
            state["number_game_count"] += 1
            state["session_games"].append("number")
            state["number_guess_min"] = 1
            state["number_guess_max"] = 50
            state["_next"] = "menu"
        else:
            state["_next"] = "start_number_game"

    return state
