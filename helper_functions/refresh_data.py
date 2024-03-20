from .pull_game_logic import pull_game, WrongSportException
from .game_states_logic import get_play_states
from tqdm import tqdm
import time
import numpy as np
import pandas as pd
import datetime as dt
import requests
import json
import os

def find_new_game_ids(start_date, end_date):
    """
    Retrieves the list of game IDs from the NCAA website for basketball men's D1 dashboard 
    between the specified start and end dates.

    Args:
        start_date (datetime): The start date (inclusive) to fetch game IDs.
        end_date (datetime): The end date (inclusive) to fetch game IDs.

    Returns:
        list: A list of game IDs found between the start_date and end_date.

    Example:
        >>> start = datetime.datetime(2024, 3, 15)
        >>> end = datetime.datetime(2024, 3, 20)
        >>> game_ids = find_new_game_ids(start, end)
        >>> print(game_ids)
    """
    start_date = start_date.date()
    end_date = end_date.date()

    delta = end_date - start_date   # returns timedelta
    date_strings = [(start_date + dt.timedelta(days=x)).strftime('%Y/%m/%d') for x in range(delta.days + 1)]

    new_index_list = []
    for x in date_strings:
        url = f"https://data.ncaa.com/casablanca/scoreboard/basketball-men/d1/{x}/scoreboard.json"
        r = requests.get(url)
        if r.status_code == 404:
            continue
        else:
            new_index_list += [x['game']['gameID'] for x in json.loads(r.content)['games']]
    return new_index_list

def save_down_games(id_list, target_dir, diagnose=True):
    """
    Loops through a list of game IDs to pull game data and saves it to the target directory.

    Args:
        id_list (list): A list of game IDs to be processed and saved.
        target_dir (str): The directory where the game data will be saved.
        diagnose (bool, optional): If True, the function will return a list of encountered errors. 
                                   Defaults to True.

    Returns:
        list: A list of encountered errors during the process. It's returned only if diagnose is True.

    Note:
        - The game data is saved as Excel files in the target directory.
        - If diagnose is True, the function will collect and return a list of encountered errors.

    Example:
        >>> error_list = save_down_games(['game_id1', 'game_id2'], '/path/to/target_dir', diagnose=True)
        >>> if error_list:
        >>>     print("Encountered errors during processing:", error_list)
    """
    if diagnose:
        error_list = []
        error_id = []

    for game_id in id_list:
        try:
            try:
                current_data = pull_game(game_id)  # Assuming pull_game function is defined elsewhere
                current_data['data'].to_excel('{}/{}'.format(target_dir, current_data['id'] + '.xlsx'), index=False)
            except WrongSportException:
                pass
        except Exception as e:
            if diagnose:
                error_list.append(e)
                error_id.append(game_id)

    if diagnose:
        return error_id, error_list
    
def read_latest_transition_file(latest_transition_file):
    return pd.read_csv(latest_transition_file)
    
def save_valid_transitions(transition_file, file_version):

    """
    Checks and saves valid transitions from game data to a CSV file.

    Args:
        transition_file (DataFrame): DataFrame containing transition data.
        file_version (str): Latest version of the transition file to be saved. 
                            This will typically be '06' the first time.

    Returns:
        int: Returns 1 if the saving process is successful.

    Notes:
        - The function assumes the existence of a 'Team_Names_Abbrs_v02.xlsx' file.
        - The function assumes the existence of a 'raw_game_pulls' directory containing game data.
        - Valid transitions are determined based on predefined criteria.
        - The resulting DataFrame is saved as a CSV file named 'ALL_VALID_TRANSITIONS_v{file_version}.csv'.

    Example:
        >>> save_valid_transitions(transition_data, '06')
    """
    team_database = pd.read_excel('Team_Names_Abbrs_v02.xlsx')
    files_read = list(transition_file['filename'].unique())
    for filename in os.listdir('raw_game_pulls'):
        teams = filename.split('for ')[1].split('.xlsx')[0]
        team1, team2 = teams.split(' vs ')
        reduce_df = team_database[team_database['name']==team1].copy()
        if len(reduce_df) > 1:
            print('Collision with {}'.format(team1))
            return 0
        elif len(reduce_df) == 0:
            print('No match for {}'.format(team1))
            return 0

        reduce_df = team_database[team_database['name']==team2].copy()
        if len(reduce_df) > 1:
            print('Collision with {}'.format(team2))
            return 0
        elif len(reduce_df) == 0:
            print('No match for {}'.format(team2))
            return 0
        
    #PROCESS NEW GAMES
    #initialize full dataframe
    final_df = pd.DataFrame()

    #iterate through files
    for filename in tqdm(os.listdir('raw_game_pulls')):
        if filename not in files_read:
            #initialize individual game dataframe
            game_tracking_df = pd.DataFrame()

            #parse filename
            teams = filename.split('for ')[1].split('.xlsx')[0]
            team1, team2 = teams.split(' vs ')
            team_A = team_database[team_database['name']==team1]['abbreviations'].values[0]
            team_B = team_database[team_database['name']==team2]['abbreviations'].values[0]

            #pull file data
            current_data = pd.read_excel('raw_game_pulls/{}'.format(filename))

            #quick check that the abbrev is in there 
            #(had to manually change some because abbrev changed throughout season)
            all_text = ' '.join(list(current_data['PLAY']))
            try:
                assert team_A in all_text
            except Exception:
                print('{} not in {}'.format(team_A, filename))
                break
            try:
                assert team_B in all_text
            except Exception:
                print('{} not in {}'.format(team_B, filename))
                break


            #pull states
            all_states = get_play_states(current_data, team_A, team_B)
            final_game = pd.DataFrame()
            for i in range(len(all_states)):
                half_tuples = all_states[i]

                #just take play, not timestamp
                smaller_list = [x[0] for x in half_tuples if x[0] != 'UNNEC']

                #that means rather than this logic, we should count the transitions in here

                # curr_half = pd.DataFrame(smaller_list, columns = ['State','Time'])
                # curr_half['Period']=i+1
                # final_game = pd.concat([final_game,curr_half])

                list_of_pairs = [tuple(smaller_list[j:j+2]) for j in range(len(smaller_list)-2)]

                curr_half = pd.DataFrame({'Transition': list_of_pairs})
                curr_half['Period']=i+1
                game_tracking_df=pd.concat([game_tracking_df,curr_half]).reset_index(drop=True)
            game_tracking_df['filename']=filename
            final_df=pd.concat([final_df,game_tracking_df]).reset_index(drop=True)

    #delete all transitions from FREETHROW state that don't result in either team r or opposite team i
    #also delete when freethrow turns to i2 or i3
    validate = []
    for i in range(len(final_df)):
        curr_tran = final_df['Transition'][i]
        if curr_tran in [('Bi1', 'Af3'),
                        ('Ai2', 'Bf3'),
                        ('Af0', 'Af3'),
                        ('Ai0', 'Bf3'),
                        ('Bf2', 'Bf2'),
                        ('Bi3', 'Af3'),
                        ('Ai0', 'Bf2'),
                        ('Bf3', 'Bf0'),
                        ('Af3', 'Af1'),
                        ('Af3', 'Af0'),
                        ('Bf0', 'Bf2'),
                        ('Bf3', 'Bf1'),
                        ('Ai1', 'Bf3'),
                        ('Br0', 'Af3'),
                        ('Ar0', 'Bf3'),
                        ('Af0', 'Af2'),
                        ('Ai3', 'Bf2'),
                        ('Bi3', 'Af2'),
                        ('Bf2', 'Bf1'),
                        ('Bf2', 'Bf0'),
                        ('Ai2', 'Bf2'),
                        ('Ai1', 'Bf2'),
                        ('Af2', 'Af1'),
                        ('Bi0', 'Af2'),
                        ('Bi2', 'Af2'),
                        ('Af2', 'Af0'),
                        ('Bi1', 'Af2'),
                        ('Bi3', 'Bi3'),
                        ('Ai3', 'Ai3'),
                        ('Ai0', 'Ai3'),
                        ('Bi0', 'Bi3'),
                        ('Ai2', 'Ai3'),
                        ('Ai3', 'Ai2'),
                        ('Ai3', 'Bf0'),
                        ('Br0', 'Af2'),
                        ('Ar0', 'Bf2'),
                        ('Ai1', 'Ai3'),
                        ('Bi3', 'Af0'),
                        ('Bi0', 'Af0'),
                        ('Ai0', 'Ai2'),
                        ('Ai1', 'Bf0'),
                        ('Bi3', 'Bi2'),
                        ('Ai0', 'Bf0'),
                        ('Ai2', 'Ai2'),
                        ('Bi1', 'Bi3'),
                        ('Bi0', 'Bi2'),
                        ('Bi2', 'Bi3'),
                        ('Bi1', 'Af0'),
                        ('Br0', 'Bi3'),
                        ('Ai1', 'Ai2'),
                        ('Bi2', 'Bi2'),
                        ('Bi1', 'Bi2'),
                        ('Ai2', 'Bf0'),
                        ('Ar0', 'Ai3'),
                        ('Bi2', 'Af0'),
                        ('Br0', 'Bi2'),
                        ('Br0', 'Af0'),
                        ('Ar0', 'Ai2'),
                        ('Ar0', 'Bf0'),
                        ('Bi2','Af3'),
                        ('Af3','Af2')]:
            validate.append(False)

        elif ('f' in curr_tran[0])&('f' in curr_tran[1]):
            if (('A' in curr_tran[0])&('A' in curr_tran[1])) | (('B' in curr_tran[0])&('B' in curr_tran[1])):
                validate.append(True)
            else:
                validate.append(False)
        elif (('Af' in curr_tran[0])&('Ai' in curr_tran[1])) | (('Bf' in curr_tran[0])&('Bi' in curr_tran[1])):
            validate.append(False)
        elif ('f' in curr_tran[0])&(('i3' in curr_tran[1]) | ('i2' in curr_tran[1])):
            validate.append(False)
        elif ('1' in curr_tran[1])&('f' not in curr_tran[0]):
            validate.append(False)
        else:
            validate.append(True)
    final_df['is_valid']=validate
    valid_df = final_df[final_df['is_valid']==True].copy().reset_index(drop=True)
    to_save = pd.concat([transition_file,valid_df]).copy().reset_index(drop=True)
    to_save.to_csv('../ALL_VALID_TRANSITIONS_v{}.csv'.format(file_version),index=False)
    return 1