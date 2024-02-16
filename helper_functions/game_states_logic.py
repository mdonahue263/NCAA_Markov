#going to still iterate through game indices - each function will take in a PLAY (will have issues when multiple plays required)
import pandas as pd
import regex as re

def get_play_states(game_df, team_A, team_B):
    """
    Main function to iterate through game DF and return each state label

    args: game_df - pandas DataFrame containing TIME, PLAY, etc.

    returns: new_states: list of states
    """
    new_states = []

    for idx in range(len(game_df)):
        new_states.append(perform_logic(game_df, idx, team_A, team_B))
    
    
    return new_states

def is_unnec(play):
    """
    Check list of plays which will automatically result in UNNEC outcome
    args: play: STR - description of play result

    return: BOOL, True if unnecessary
    """

    bad_words = ['MISSED','Steal','Assist','Block','Subbing','timeout','time out']
    matching=re.compile('|'.join(bad_words))

    if matching.search(play):
        return True
    else:
        return False
    
def foul_logic(game_df, idx, team_A, team_B):
    """
    Work through possible scenarios when FOUL is involved in the play
    args: idx: INT - current DataFrame index

    returns: new_state: STR - new state
    """

    #if foul happens, we need the next play to determine what the result is
    #Will need to amend if the shot is GOOD before the foul?
    #Confirmed - if shot is GOOD before the foul, then foul results in UNNEC and previous line results in f2 or f3
    #Also need to check timestamp before foul - can have GOOD shot on previous separate play
    #may need to do same backwards iteration to find "valid plays"

    current_play=game_df['PLAY'][idx]
    curr_time=game_df['TIME'][idx]
    prev_play='Filler String'
    prev_time = 'Filler String'

    try:
        prev_play = game_df['PLAY'][idx-1]
        prev_time = game_df['TIME'][idx-1]
    except KeyError:
        pass

    if ('GOOD' in prev_play) & (curr_time==prev_time):
        new_state = 'UNNEC'

    #sadly, we need to account for subs and timeouts in between foul and FTs
        
    else:
        play_iterator=1
        valid_play = False
        while not valid_play:
            next_play = game_df['PLAY'][idx+play_iterator]
            if ('Sub' in next_play) | ('timeout' in next_play) | ('time out' in next_play):
                valid_play=False
                play_iterator+=1
            else:
                valid_play=True

        if 'Free Throw' in next_play:
            if team_A in current_play:
                new_state = 'Bf0'
            else:
                new_state = 'Af0'
        else:
            if team_A in current_play:
                new_state = 'Bi0'
            else:
                new_state = 'Ai0'

    return new_state

def free_throw_good_logic(game_df, idx, team_A, team_B):
    """
    Work through possible scenarios when MADE FREE THROW is involved in the play
    args: idx: INT - current DataFrame index

    returns: new_state: STR - new state
    """

    #if free throw is made, we need the next play to determine if next play is FT or inbound
    #sadly, we need to account for subs and timeouts in between FTs
    #NOTE - THIS WILL BE DIFFERENT WITH TECHNICAL FOULS

    current_play=game_df['PLAY'][idx]
    play_iterator=1
    valid_play = False

    while not valid_play:
        next_play = game_df['PLAY'][idx+play_iterator]
        if ('Sub' in next_play) | ('timeout' in next_play) | ('time out' in next_play):
            valid_play=False
            play_iterator+=1
        else:
            valid_play=True

    if 'Free Throw' in next_play:
        if team_A in current_play:
            new_state = 'Af1'
        else:
            new_state = 'Bf1'
    else:
        if team_A in current_play:
            new_state = 'Bi1'
        else:
            new_state = 'Ai1'
    return new_state


def rebound_logic(game_df, idx, team_A, team_B):
    """
    Work through possible scenarios when REBOUND is involved in the play
    args: idx: INT - current DataFrame index

    returns: new_state: STR - new state
    """
    #if rebound on DEAD BALL, this either transitions to same team FT OR non-shooting foul so inbound?
    #Try this - if previous play is "Free Throw MISSED" then transitions to same team FT. Else to inbound.
    current_play=game_df['PLAY'][idx]

    try:
        prev_play = game_df['PLAY'][idx-1]
    except KeyError:
        pass
    
    if 'dead ball' in current_play:
        if "Free Throw MISSED" in prev_play:
            if team_A in current_play:
                new_state = 'Af0'
            else:
                new_state = 'Bf0'
        else:
            if team_A in current_play:
                new_state = 'Ai0'
            else:
                new_state = 'Bi0'
    else:
        if team_A in current_play:
            new_state = 'Ar0'
        else:
            new_state = 'Br0'
    return new_state

def turnover_logic(game_df, idx, team_A, team_B):
    """
    Work through possible scenarios when TURNOVER is involved in the play
    args: idx: INT - current DataFrame index

    returns: new_state: STR - new state
    """
    #treating turnovers as rebounds to simplify state space

    current_play=game_df['PLAY'][idx]

    if team_A in current_play:
        return 'Br0'
    else:
        return 'Ar0'
    


def good_shot_logic(game_df, idx, team_A, team_B):
    """
    NOTE - ENCOUNTERED PROBLEMS when GOOD results in FOUL (And 1) - may have to alter logic on last part

    Work through possible scenarios when shot GOOD is involved in the play
    args: idx: INT - current DataFrame index

    returns: new_state: STR - new state
    """
    current_play=game_df['PLAY'][idx]

    #determine point value
    pv=0
    if 'Jumper' in current_play:
        pv=2
    elif '3 Pointer' in current_play:
        pv=3
    elif 'Layup' in current_play:
        pv=2
    elif 'Dunk' in current_play:
        pv=2
    #Need to check next play for FOUL AND TIMESTAMP
    current_time = game_df['TIME'][idx]

    #this will fail if it is last play of game
    next_play = game_df['PLAY'][idx+1]
    next_time = game_df['TIME'][idx+1]

    current_time_split = current_time.split(':')
    next_time_split = next_time.split(':')

    current_time_int = int(current_time_split[0])*60 + int(current_time_split[1])
    next_time_int = int(next_time_split[0])*60 + int(next_time_split[1])

    time_between = next_time_int - current_time_int
    #### IF ASSIST, NEED TO CHECK FOLLOWING PLAY ##################################################################################
    if (('Foul' in next_play)|('Assist' in next_play)) & (time_between <= 3):
        if team_A in current_play:
            new_state = 'Af{}'.format(str(pv))
        else:
            new_state = 'Bf{}'.format(str(pv))
    else:
        if team_A in current_play:
            new_state = 'Bi{}'.format(str(pv))
        else:
            new_state = 'Ai{}'.format(str(pv))
    return new_state



def perform_logic(game_df, idx, team_A, team_B):
    """
    Function performed on each line of game DF to determine individual outcome
    args: idx: INT - current DataFrame index

    returns: new_state: STR - new state
    """
    
    current_play = game_df['PLAY'][idx]

    if is_unnec(current_play):
        return 'UNNEC'
    elif 'Foul' in current_play:
        return foul_logic(game_df, idx, team_A, team_B)
    elif "Free Throw GOOD" in current_play:
        return free_throw_good_logic(game_df, idx, team_A, team_B)
    elif "REBOUND" in current_play:
        return rebound_logic(game_df, idx, team_A, team_B)
    elif "Turnover" in current_play:
        return turnover_logic(game_df, idx, team_A, team_B)
    elif "GOOD" in current_play:
        return good_shot_logic(game_df, idx, team_A, team_B)
    else:
        return "MISSED ALL LOGIC"