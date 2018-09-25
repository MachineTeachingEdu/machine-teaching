def score(team_one, team_two):
    if team_one > team_two:
        return "Team One scores 3 points and Team Two scores 0 points."
    elif team_one < team_two:
        return "Team Two scores 3 points and Team One scores 0 points."
    else:   #Game must be a draw if the previous two if statements are false
        return "Both Team One and Team Two score 1 point."
