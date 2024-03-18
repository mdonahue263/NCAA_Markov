import pandas as pd
import pickle
import os
from tqdm import tqdm
from helper_functions.simulate_game import simulate_game
from helper_functions.combine_matrices import combine_team_matrix
import numpy as np

with open('helper_functions/avg_input_matrix.pickle', 'rb') as file:
    avg_input_matrix = pickle.load(file)

with open('helper_functions/std_input_matrix.pickle', 'rb') as file:
    std_input_matrix = pickle.load(file)

with open('models/nn1.pickle', 'rb') as file:
    nn1=pickle.load(file)




def matchup(team_A, team_B, strategy='sim', reps=1, argmax=False):
    matrix_A = pd.read_excel('team_specific_matrix/{}_A.xlsx'.format(team_A), index_col='Starting_State')
    matrix_B = pd.read_excel('team_specific_matrix/{}_B.xlsx'.format(team_B), index_col='Starting_State')

    if strategy == 'sim':
        transition_matrix = combine_team_matrix(matrix_A, matrix_B)
        result = simulate_game(transition_matrix, reps)
        return result[1]
    elif strategy == 'nn1':
        return nn_output(nn1, team_A, team_B, reps, argmax)
    
def nn_output(model, team_A, team_B, num_sims, argmax=False):
    #Pull and Convert test matrices to numpy arrays
    matrix_A_raw = pd.read_excel('team_specific_matrix/{}_A.xlsx'.format(team_A), index_col='Starting_State')
    matrix_B_raw = pd.read_excel('team_specific_matrix/{}_B.xlsx'.format(team_B), index_col='Starting_State')


    matrix_A_normal = (matrix_A_raw - avg_input_matrix) / std_input_matrix
    matrix_A_normal=matrix_A_normal.fillna(0.)

    matrix_B_normal = (matrix_B_raw - avg_input_matrix) / std_input_matrix
    matrix_B_normal=matrix_B_normal.fillna(0.)

    test_matrix_a_array = matrix_A_normal.values.reshape(-1, 18, 18)
    test_matrix_b_array = matrix_B_normal.values.reshape(-1, 18, 18)

    predictions = model.predict([test_matrix_a_array, test_matrix_b_array], verbose=0)

    if argmax:
        a_score, b_score = (np.argmax(predictions[0]), np.argmax(predictions[1]))
        if a_score == b_score:
            winner=np.random.choice([1,2])
            if winner == 1:
                a_score += 1
            else:
                b_score += 1
        predicted_score = (a_score, b_score)
        return [predicted_score]
    
    else:
        home_scores = list(np.random.choice(np.arange(1,202), num_sims, p=predictions[0][0]))
        away_scores = list(np.random.choice(np.arange(1,202), num_sims, p=predictions[1][0]))

        for s in range(len(home_scores)):
            if home_scores[s] == away_scores[s]:
                winner=np.random.choice([1,2])
                if winner == 1:
                    home_scores[s]+=1
                else:
                    away_scores[s]+=1

        return list(zip(home_scores, away_scores))
    
def simulate_tournament(strategy='sim', reps=10):
    """
    Simualte entire tournament.
    Strategy: currently sim or nn1
    Reps: number of times to simulate each game
    """

    te1='UConn'
    te2='Iowa St.'
    te3='Illinois'
    te4='Auburn'
    te5='San Diego St.'
    te6='BYU'
    te7='Washington St.'
    te8='Fla. Atlantic'
    te9='Northwestern'
    te10='Drake'
    te11='Duquesne'
    te12='UAB'
    te13='Yale'
    te14='Morehead St.'
    te15='South Dakota St.'
    te16='Stetson'

    tw1='North Carolina'
    tw2='Arizona'
    tw3='Baylor'
    tw4='Alabama'
    tw5="Saint Mary's (CA)"
    tw6='Clemson'
    tw7='Dayton'
    tw8='Mississippi St.'
    tw9='Michigan St.'
    tw10='Nevada'
    tw11='New Mexico'
    tw12 = 'Grand Canyon'
    tw13='Col. of Charleston'
    tw14='Colgate'
    tw15='Long Beach St.'
    tw16='Howard'

    ts1='Houston'
    ts2 = 'Marquette'
    ts3='Kentucky'
    ts4='Duke'
    ts5='Wisconsin'
    ts6='Texas Tech'
    ts7='Florida'
    ts8='Nebraska'
    ts9='Texas A&M'
    ts10='Boise St.'
    ts11='NC State'
    ts12='James Madison'
    ts13='Vermont'
    ts14 = 'Oakland'
    ts15='Western Ky.'
    ts16='Longwood'

    tm1='Purdue'
    tm2='Tennessee'
    tm3='Creighton'
    tm4='Kansas'
    tm5='Gonzaga'
    tm6='South Carolina'
    tm7='Texas'
    tm8='Utah St.'
    tm9='TCU'
    tm10='Virginia'
    tm11='Oregon'
    tm12='McNeese'
    tm13='Samford'
    tm14='Akron'
    tm15="Saint Peter's"
    tm16='Grambling'

    validate_entries=input('Play ins: Howard, Boise State, Grambling, and UVA ok? y/n ')
    if validate_entries == 'y':
        pass
    else:
        h_w = input('Howard or Wagner? h/w ')
        if h_w == 'h':
            tw16='Howard'
        elif h_w == 'w':
            tw16 = 'Wagner'

        b_c = input('Boise State or Colorado? b/c ')
        if b_c == 'b':
            ts10='Boise St.'
        elif b_c == 'c':
            ts10 = 'Colorado'
        
        g_m = input('Grambling or Montana St? g/m ')
        if g_m == 'g':
            tm16 = 'Grambling'
        elif g_m == 'm':
            tm16='Montana St.'

        v_c = input('UVA or Colorado State? v/c ')
        if v_c == 'v':
            tm10='Virginia'
        elif v_c == 'c':
            tm10 = 'Colorado St.'

    
    eastern_bracket = [(te1,te16),
                        (te8,te9),
                        (te5,te12),
                        (te4,te13),
                        (te6,te11),
                        (te3,te14),
                        (te7,te10),
                        (te2,te15)]

    western_bracket = [(tw1,tw16),
                        (tw8,tw9),
                        (tw5,tw12),
                        (tw4,tw13),
                        (tw6,tw11),
                        (tw3,tw14),
                        (tw7,tw10),
                        (tw2,tw15)]

    southern_bracket = [(ts1,ts16),
                        (ts8,ts9),
                        (ts5,ts12),
                        (ts4,ts13),
                        (ts6,ts11),
                        (ts3,ts14),
                        (ts7,ts10),
                        (ts2,ts15)]

    midwestern_bracket = [(tm1,tm16),
                        (tm8,tm9),
                        (tm5,tm12),
                        (tm4,tm13),
                        (tm6,tm11),
                        (tm3,tm14),
                        (tm7,tm10),
                        (tm2,tm15)]

    first_round = [eastern_bracket, western_bracket, southern_bracket, midwestern_bracket]

    #RUN FIRST ROUND
    #try with 10 simulations
    east_round_2 = []
    west_round_2 = []
    south_round_2 = []
    midwest_round_2 = []
    second_round = [east_round_2,west_round_2,south_round_2,midwest_round_2]

    for division_number in range(len(first_round)):
        for match in first_round[division_number]:
            print('Matchup: {} vs. {}'.format(match[0], match[1]))

            #simulate matchup from both sides and put in one list, find mean
            res=matchup(match[0],match[1], strategy, reps)
            w1=[x[0]>x[1] for x in res]
            res2=matchup(match[1],match[0], strategy, reps)
            w2=[x[0]<x[1] for x in res]
            winners = np.mean(w1+w2)

            #if even, do one extra simulation
            if winners == 0.5:
                res=matchup(match[0],match[1], strategy)
                winners=res[0][0]>res[0][1]
            if winners > 0.5:
                print('{} wins'.format(match[0]))
                second_round[division_number].append(match[0])
            else:
                print('{} wins'.format(match[1]))
                second_round[division_number].append(match[1])
            print()
        print('-------------------------------------------------------------------------')

        #second round is listed, now needs formatting
    for n in range(len(second_round)):
        second_round[n] = [(second_round[n][2*x],second_round[n][2*x+1]) for x in range(len(second_round[n])//2)]

    #RUN SECOND ROUND
    east_round_3 = []
    west_round_3 = []
    south_round_3 = []
    midwest_round_3 = []
    third_round = [east_round_3,west_round_3,south_round_3,midwest_round_3]

    for division_number in range(len(second_round)):
        for match in second_round[division_number]:
            print('Matchup: {} vs. {}'.format(match[0], match[1]))

            #simulate matchup from both sides and put in one list, find mean
            res=matchup(match[0],match[1], strategy, reps)
            w1=[x[0]>x[1] for x in res]
            res2=matchup(match[1],match[0], strategy, reps)
            w2=[x[0]<x[1] for x in res]
            winners = np.mean(w1+w2)

            #if even, do one extra simulation
            if winners == 0.5:
                res=matchup(match[0],match[1], strategy)
                winners=res[0][0]>res[0][1]
            if winners > 0.5:
                print('{} wins'.format(match[0]))
                third_round[division_number].append(match[0])
            else:
                print('{} wins'.format(match[1]))
                third_round[division_number].append(match[1])
            print()
        print('----------------------------------------------------------------')

    #third round is listed, now needs formatting
    for n in range(len(third_round)):
        third_round[n] = [(third_round[n][2*x],third_round[n][2*x+1]) for x in range(len(third_round[n])//2)]


    #RUN THIRD ROUND
    east_round_4 = []
    west_round_4 = []
    south_round_4 = []
    midwest_round_4 = []
    fourth_round = [east_round_4,west_round_4,south_round_4,midwest_round_4]

    for division_number in range(len(third_round)):
        for match in third_round[division_number]:
            print('Matchup: {} vs. {}'.format(match[0], match[1]))

            #simulate matchup from both sides and put in one list, find mean
            res=matchup(match[0],match[1], strategy, reps)
            w1=[x[0]>x[1] for x in res]
            res2=matchup(match[1],match[0], strategy, reps)
            w2=[x[0]<x[1] for x in res]
            winners = np.mean(w1+w2)

            #if even, do one extra simulation
            if winners == 0.5:
                res=matchup(match[0],match[1], strategy)
                winners=res[0][0]>res[0][1]
            if winners > 0.5:
                print('{} wins'.format(match[0]))
                fourth_round[division_number].append(match[0])
            else:
                print('{} wins'.format(match[1]))
                fourth_round[division_number].append(match[1])
            print()
        print('------------------------------------------------------------------')


    final_four = []
    for match in fourth_round:
        print('Matchup: {} vs. {}'.format(match[0], match[1]))

        #simulate matchup from both sides and put in one list, find mean
        res=matchup(match[0],match[1], strategy, reps)
        w1=[x[0]>x[1] for x in res]
        res2=matchup(match[1],match[0], strategy, reps)
        w2=[x[0]<x[1] for x in res]
        winners = np.mean(w1+w2)

        #if even, do one extra simulation
        if winners == 0.5:
            res=matchup(match[0],match[1], strategy)
            winners=res[0][0]>res[0][1]
        if winners > 0.5:
            print('{} wins'.format(match[0]))
            final_four.append(match[0])
        else:
            print('{} wins'.format(match[1]))
            final_four.append(match[1])
        print()

    #FINAL FOUR
    finals=[]
    team_A = final_four[0]
    team_B = final_four[1]
    print('Matchup: {} vs. {}'.format(team_A, team_B))

    #simulate matchup from both sides and put in one list, find mean
    res=matchup(team_A,team_B, strategy, reps)
    w1=[x[0]>x[1] for x in res]
    res2=matchup(team_B,team_A, strategy, reps)
    w2=[x[0]<x[1] for x in res]
    winners = np.mean(w1+w2)

    #if even, do one extra simulation
    if winners == 0.5:
        res=matchup(team_A,team_B,strategy)
        winners=res[0][0]>res[0][1]
    if winners > 0.5:
        print('{} wins'.format(team_A))
        finals.append(team_A)
    else:
        print('{} wins'.format(team_B))
        finals.append(team_B)
    print()

    team_A = final_four[2]
    team_B = final_four[3]
    print('Matchup: {} vs. {}'.format(team_A, team_B))

    #simulate matchup from both sides and put in one list, find mean
    res=matchup(team_A,team_B, strategy, reps)
    w1=[x[0]>x[1] for x in res]
    res2=matchup(team_B,team_A, strategy, reps)
    w2=[x[0]<x[1] for x in res]
    winners = np.mean(w1+w2)

    #if even, do one extra simulation
    if winners == 0.5:
        res=matchup(team_A,team_B, strategy)
        winners=res[0][0]>res[0][1]
    if winners > 0.5:
        print('{} wins'.format(team_A))
        finals.append(team_A)
    else:
        print('{} wins'.format(team_B))
        finals.append(team_B)
    print()



    total_reps=reps*2
    total_ou = 0
    print('Matchup: {} vs. {}'.format(finals[0], finals[1]))

    #simulate matchup from both sides and put in one list, find mean
    res=matchup(finals[0],finals[1], strategy, reps)
    w1=[x[0]>x[1] for x in res]
    res2=matchup(finals[1],finals[0], strategy, reps)
    w2=[x[0]<x[1] for x in res]
    winners = np.mean(w1+w2)

    
    for score in res:
        total_ou += score[0] + score[1]

    for score in res2:
        total_ou += score[0] + score[1]

    #if even, do one extra simulation
    if winners == 0.5:
        res=matchup(finals[0],finals[1], strategy)
        total_ou += res[0][0] + res[0][1]
        total_reps+=1
        winners=res[0][0]>res[0][1]
    if winners > 0.5:
        print('{} wins'.format(finals[0]))
        final_four.append(finals[0])
    else:
        print('{} wins'.format(finals[1]))
        final_four.append(finals[1])
    print()
    print('Tiebreaker O/U: {}'.format(total_ou//total_reps))