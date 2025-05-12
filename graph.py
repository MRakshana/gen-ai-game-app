{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bcf86ee0",
   "metadata": {},
   "outputs": [],
   "source": [
    "from langgraph.graph import END, StateGraph\n",
    "from typing import TypedDict, Optional\n",
    "\n",
    "class GameState(TypedDict):\n",
    "    guess: Optional[str]\n",
    "    correct_number: str\n",
    "    message: Optional[str]\n",
    "    end: bool\n",
    "\n",
    "# Define nodes\n",
    "def start_game(state: GameState) -> GameState:\n",
    "    state[\"correct_number\"] = \"5\"  # fixed for simplicity\n",
    "    state[\"message\"] = \"Guess a number between 1 and 10:\"\n",
    "    return state\n",
    "\n",
    "def check_guess(state: GameState) -> GameState:\n",
    "    if state[\"guess\"] == state[\"correct_number\"]:\n",
    "        state[\"message\"] = \"🎉 Correct! You win!\"\n",
    "        state[\"end\"] = True\n",
    "    else:\n",
    "        state[\"message\"] = f\"❌ Incorrect. Try again!\"\n",
    "        state[\"end\"] = False\n",
    "    return state\n",
    "\n",
    "# Build graph\n",
    "def build_graph():\n",
    "    builder = StateGraph(GameState)\n",
    "\n",
    "    builder.add_node(\"start\", start_game)\n",
    "    builder.add_node(\"check\", check_guess)\n",
    "\n",
    "    builder.set_entry_point(\"start\")\n",
    "\n",
    "    builder.add_edge(\"start\", \"check\")\n",
    "   builder.add_edge("check", END
    "    )\n",
    "\n",
    "    return builder.compile()\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
