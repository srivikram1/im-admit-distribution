import streamlit as st

# Admit Distribution Function
def distribute_admits(day_of_week, overnight_admits, team_a, long_call, short_call, rounds):
    assigned = {"team_a": 0, "long_call": 0, "short_call": 0, "rounds": 0}
    log = []

    if day_of_week == 1:  # Monday
        rounds_soft, rounds_hard, rounds_max = 14, 14, 3
    else:
        rounds_soft, rounds_hard, rounds_max = 10, 10, 2
    long_soft, long_hard, long_max = 8, 14, 4
    short_soft, short_hard, short_max = 12, 14, 4
    team_a_hard = 36

    rotation = ["rounds", "long_call", "short_call"]

    # Overflow adjustment
    everyone_over_cap = rounds > rounds_hard and long_call > long_hard and short_call > short_hard and team_a > team_a_hard
    if not everyone_over_cap:
        if long_call > long_hard:
            overflow = long_call - long_hard
            long_call = long_hard
            overnight_admits += overflow
        if short_call > short_hard:
            overflow = short_call - short_hard
            short_call = short_hard
            overnight_admits += overflow

    if day_of_week == 2:  # Tuesday special rules
        while overnight_admits > 0 and (long_call < 14 or short_call < 14):
            if long_call <= short_call and long_call < 14:
                assigned["long_call"] += 1
                long_call += 1
                overnight_admits -= 1
                log.append(("Priority1", "long_call"))
            elif short_call < 14:
                assigned["short_call"] += 1
                short_call += 1
                overnight_admits -= 1
                log.append(("Priority1", "short_call"))
        while overnight_admits > 0 and rounds < 10 and assigned["rounds"] < 2:
            assigned["rounds"] += 1
            rounds += 1
            overnight_admits -= 1
            log.append(("Priority2", "rounds"))
        if overnight_admits > 0 and team_a < 36:
            take = min(overnight_admits, 36 - team_a)
            assigned["team_a"] += take
            team_a += take
            overnight_admits -= take
            log.append(("Priority3", "team_a"))
        p4_cycle = ["long_call", "short_call", "team_a", "rounds"]
        idx = 0
        while overnight_admits > 0:
            team = p4_cycle[idx % 4]
            assigned[team] += 1
            if team == "long_call": long_call += 1
            elif team == "short_call": short_call += 1
            elif team == "team_a": team_a += 1
            elif team == "rounds": rounds += 1
            overnight_admits -= 1
            log.append(("Priority4 overflow", team))
            idx += 1
    else:
        i = 0
        while overnight_admits > 0:
            assigned_this_rotation = 0
            for team in rotation:
                if team == "rounds" and rounds < rounds_soft and assigned["rounds"] < rounds_max:
                    assigned["rounds"] += 1
                    rounds += 1
                    overnight_admits -= 1
                    assigned_this_rotation += 1
                    log.append(("Priority1", "rounds"))
                elif team == "long_call" and long_call < long_soft and assigned["long_call"] < long_max:
                    assigned["long_call"] += 1
                    long_call += 1
                    overnight_admits -= 1
                    assigned_this_rotation += 1
                    log.append(("Priority1", "long_call"))
                elif team == "short_call" and short_call < short_soft and assigned["short_call"] < short_max:
                    assigned["short_call"] += 1
                    short_call += 1
                    overnight_admits -= 1
                    assigned_this_rotation += 1
                    log.append(("Priority1", "short_call"))
            if assigned_this_rotation == 0:
                to_team_a = min(overnight_admits, team_a_hard - team_a)
                if to_team_a > 0:
                    assigned["team_a"] += to_team_a
                    team_a += to_team_a
                    overnight_admits -= to_team_a
                    log.append(("Priority1 remainder → team_a", to_team_a))
                break
        if overnight_admits > 0 and team_a >= team_a_hard:
            while overnight_admits > 0 and (rounds < rounds_hard or long_call < long_hard or short_call < short_hard):
                for team in rotation:
                    if team == "rounds" and rounds < rounds_hard:
                        assigned["rounds"] += 1
                        rounds += 1
                        overnight_admits -= 1
                        log.append(("Priority2", "rounds"))
                    elif team == "long_call" and long_call < long_hard:
                        assigned["long_call"] += 1
                        long_call += 1
                        overnight_admits -= 1
                        log.append(("Priority2", "long_call"))
                    elif team == "short_call" and short_call < short_hard:
                        assigned["short_call"] += 1
                        short_call += 1
                        overnight_admits -= 1
                        log.append(("Priority2", "short_call"))
        while overnight_admits > 0:
            p3_cycle = ["rounds", "team_a", "long_call", "short_call"]
            for team in p3_cycle:
                if overnight_admits == 0:
                    break
                assigned[team] += 1
                if team == "rounds": rounds += 1
                elif team == "team_a": team_a += 1
                elif team == "long_call": long_call += 1
                elif team == "short_call": short_call += 1
                overnight_admits -= 1
                log.append(("Priority3 overflow", team))

    activation_required = False
    total_census = team_a + long_call + short_call + rounds
    if total_census >= 65:
        activation_required = True
    if team_a >= 33 or assigned["team_a"] >= 10:
        activation_required = True
    if long_call > 8 or short_call > 12 or rounds > 10:
        activation_required = True
    if assigned["long_call"] >= 3 or assigned["short_call"] >= 3 or assigned["rounds"] >= 3:
        activation_required = True
    help_attending_status = ("A. Help attending activation required"
                             if activation_required else
                             "B. Help attending activation not required")

    return assigned, team_a, long_call, short_call, rounds, log, help_attending_status

# Streamlit App
st.title("IM Admit Distribution")
day = st.number_input("Day of the week (1=Monday, 2=Tuesday, ..., 7=Sunday)", min_value=1, max_value=7, value=1)
overnight = st.number_input("Total overnight admits", min_value=0, value=0)
team_a = st.number_input("Team A current census", min_value=0, value=0)
long_call = st.number_input("Long call team census", min_value=0, value=0)
short_call = st.number_input("Short call team census", min_value=0, value=0)
rounds = st.number_input("Rounds team census", min_value=0, value=0)

if st.button("Distribute Admits"):
    assigned, fa, fl, fs, fr, log, help_status = distribute_admits(day, overnight, team_a, long_call, short_call, rounds)
    st.subheader("Admits assigned")
    st.write(assigned)
    st.subheader("Final census")
    st.write({"Long call": fl, "Short call": fs, "Rounds": fr, "Team A": fa})
    st.subheader("Step-by-step allocation")
    for entry in log:
        st.write(entry)
    st.subheader("Help attending status")
    st.write(help_status)
