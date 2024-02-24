import numpy as np
import pandas as pd
import time
from helper_functions.clean_transitions import clean_transition_column
from tqdm import tqdm

transition_times = pd.read_excel('Transition_times_reduced.xlsx')
transition_times['Transition'] = clean_transition_column(transition_times['Transition'])

#reduce time it takes by turning transition times into dict
time_dict = dict()
for t in transition_times['Transition'].unique():
    time_dict[t] = list(transition_times[transition_times['Transition'] == t]['Time'].values)

scoring = pd.read_excel('Transitions_and_scores_v2.xlsx')
scoring['Transition']=clean_transition_column(scoring['Transition'])

def choose_ending_state(t_matrix, state):
    # Get the row corresponding to the starting state
    transition_probs = t_matrix.loc[state]
    
    # Choose an ending state based on the probabilities
    ending_state = np.random.choice(transition_probs.index, p=transition_probs.values)
    
    return ending_state

def simulate_game(transition_matrix, num_games = 1, verbose = False):

    outer_df = pd.DataFrame()
    scores = []

    for nth_game in tqdm(range(num_games)):
        #separate data for firts half and second half
        first_half_events = pd.DataFrame(columns=['Transition','Team_A','Team_B','Time'])
        time_remaining=20*60
        current_state = np.random.choice(['Ai0','Bi0'])

        #simulate transitions and scores until time runs out
        while time_remaining >= 0:
            next_state = choose_ending_state(transition_matrix, current_state)
            transition = (current_state, next_state)
            possible_times = time_dict[transition]
            time_elapsed = np.random.choice(possible_times['Time'])

            time_remaining-=time_elapsed

            play_score = scoring[scoring['Transition']==transition].copy()
            play_score['Time'] = time_remaining
            first_half_events = pd.concat([first_half_events, play_score])
            current_state = next_state

        if verbose:
            first_half_events['Team_A_Final'] = first_half_events['Team_A'].cumsum()
            first_half_events['Team_B_Final'] = first_half_events['Team_B'].cumsum()

            print('Game number {}'.format(nth_game+1))
            print('First Half Result: ')
            print(first_half_events.tail(1)[['Team_A_Final','Team_B_Final']])

        second_half_events=pd.DataFrame(columns=['Transition','Team_A','Team_B','Time'])
        current_state = np.random.choice(['Ai0','Bi0'])
        time_remaining=20*60

        #simulate transitions and scores until time runs out
        while time_remaining >= 0:
            next_state = choose_ending_state(transition_matrix, current_state)
            transition = (current_state, next_state)
            possible_times = time_dict[transition]
            time_elapsed = np.random.choice(possible_times['Time'])

            time_remaining-=time_elapsed

            play_score = scoring[scoring['Transition']==transition].copy()
            play_score['Time'] = time_remaining
            second_half_events = pd.concat([second_half_events, play_score])
            current_state = next_state

        first_half_events['Period']=1
        second_half_events['Period']=2

        final_df = pd.concat([first_half_events,second_half_events]).reset_index(drop=True)

        final_df['Team_A_Final'] = final_df['Team_A'].cumsum()
        final_df['Team_B_Final'] = final_df['Team_B'].cumsum()

        #TEST FOR TIE
        final_state = final_df.iloc[-1]
        a_score = final_state['Team_A_Final']
        b_score = final_state['Team_B_Final']

        if a_score == b_score:
            done = False
            p = 2
            if verbose:
                print('Game number {}'.format(nth_game+1))
                print('Tied at {} - {} after regulation'.format(a_score, b_score))
        else:
            done = True
            if verbose:
                print('Game number {}'.format(nth_game+1))
                print('Final score: {} - {}'.format(a_score, b_score))

        while not done:
            p+=1
            overtime_events = pd.DataFrame(columns=['Transition','Team_A','Team_B','Time'])

            time_remaining = 10*60
            while time_remaining >= 0:
                next_state = choose_ending_state(transition_matrix, current_state)
                transition = (current_state, next_state)
                possible_times = time_dict[transition]
                time_elapsed = np.random.choice(possible_times['Time'])

                time_remaining-=time_elapsed

                play_score = scoring[scoring['Transition']==transition].copy()
                play_score['Time'] = time_remaining
                overtime_events = pd.concat([overtime_events, play_score])
                current_state = next_state
            overtime_events['Period'] = p
            final_df = pd.concat([final_df,overtime_events]).reset_index(drop=True)

            final_df['Team_A_Final'] = final_df['Team_A'].cumsum()
            final_df['Team_B_Final'] = final_df['Team_B'].cumsum()

            #TEST FOR TIE
            final_state = final_df.iloc[-1]
            a_score = final_state['Team_A_Final']
            b_score = final_state['Team_B_Final']

            if a_score == b_score:
                done = False
                if verbose:
                    print('Game number {}'.format(nth_game+1))
                    print('Tied at {} - {} after overtime {}'.format(a_score, b_score, p-2))
            else:
                done = True
                if verbose:
                    print('Game number {}'.format(nth_game+1))
                    print('Final score: {} - {}'.format(a_score, b_score))
        scores.append((a_score, b_score))
        outer_df = pd.concat([outer_df, final_df])
        outer_df['Game Number'] = nth_game + 1
    return outer_df, scores
