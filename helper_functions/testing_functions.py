import numpy as np

def accuracy_distance(predicted_scores, actual_scores, distribution=False):
    real_A_score = np.array([x[0] for x in actual_scores])
    real_B_score = np.array([x[1] for x in actual_scores])

    sim_A_score=np.array([x[0] for x in predicted_scores])
    sim_B_score=np.array([x[1] for x in predicted_scores])

    
    a_error = (real_A_score-sim_A_score)**2
    b_error = (real_B_score-sim_B_score)**2

    if distribution:
        return np.sqrt(a_error+b_error)
    else:
        return np.mean(np.sqrt(a_error+b_error))
    
def accuracy_ou(predicted_scores, actual_scores, distribution=False):
    real_A_score = np.array([x[0] for x in actual_scores])
    real_B_score = np.array([x[1] for x in actual_scores])

    real_sum = real_A_score+real_B_score

    sim_A_score=np.array([x[0] for x in predicted_scores])
    sim_B_score=np.array([x[1] for x in predicted_scores])

    sim_sum=sim_A_score+sim_B_score

    if distribution:
        return sim_sum - real_sum
    else:
        return np.mean(sim_sum-real_sum)
    
def accuracy_moneyline(predicted_scores, actual_scores, distribution=False):
    real_A_score = np.array([x[0] for x in actual_scores])
    real_B_score = np.array([x[1] for x in actual_scores])

    a_won = real_A_score>real_B_score

    sim_A_score=np.array([x[0] for x in predicted_scores])
    sim_B_score=np.array([x[1] for x in predicted_scores])

    sim_A_won = sim_A_score>sim_B_score

    if distribution:
        return a_won == sim_A_won
    else:
        return np.mean(a_won == sim_A_won)