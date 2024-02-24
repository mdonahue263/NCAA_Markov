import pandas as pd

def combine_team_matrix(t1, t2, strat = 1):
    if strat == 1:
        h1 = t1[['Af0', 'Af1', 'Af2', 'Af3', 'Ai0', 'Ar0', 'Bi1', 'Bi2', 'Bi3']].copy()
        h2 = t2[['Bf0', 'Bf1', 'Bf2', 'Bf3', 'Bi0', 'Br0', 'Ai1', 'Ai2', 'Ai3']].copy()

        combined_transitions = pd.concat([h1,h2], axis=1)
    elif strat == 2:
        combined_transitions = (t1 + t2)/2

    combined_transitions = combined_transitions.div(combined_transitions.sum(axis=1), axis=0)
    return combined_transitions

    