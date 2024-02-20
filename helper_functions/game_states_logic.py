#going to still iterate through game indices - each function will take in a PLAY (will have issues when multiple plays required)
import pandas as pd
import regex as re

def get_play_states(game_df, team_A, team_B):
    """
    Main function to iterate through game DF and return each state label

    args: game_df - pandas DataFrame containing TIME, PLAY, etc.

    returns: new_states: list of states
    """

    periods = []

    for per in list(game_df['Period'].unique()):
        current_period=game_df[game_df['Period']==per].copy().reset_index(drop=True)
        new_states = []
        times=[]

        new_states.append(find_starting_state(current_period, team_A, team_B))
        if (per == 1) | (per == 2):
            times.append('20:00')
        else:
            times.append('5:00')

        for idx in range(len(current_period)):
            new_states.append(perform_logic(current_period, idx, team_A, team_B))
            times.append(current_period['TIME'][idx])
        periods.append(list(zip(new_states,times)))
    
    
    return periods

def find_starting_state(game_df, team_A, team_B):
    play_iter = 0
    done=False
    while not done:
        first_play = game_df['PLAY'][play_iter]
        if ('MISSED by' in first_play) | ('GOOD by' in first_play)| ('Turnover' in first_play) | ('takes a' in first_play):
            if team_A in first_play:
                return 'Ai0'
            else:
                return 'Bi0'
        elif 'Foul' in first_play: #bad logic but will pass - let's just say first play foul is always defensive
            if team_A in first_play:
                return 'Bi0'
            else:
                return 'Ai0'
        elif 'Subbing' in first_play:
            play_iter += 1
        else:
            print('Unknown first play:')
            print(first_play)
            raise Exception

def is_unnec(play):
    """
    Check list of plays which will automatically result in UNNEC outcome
    args: play: STR - description of play result

    return: BOOL, True if unnecessary
    """

    bad_words = ['MISSED','Steal','Assist','Block','Subbing','timeout','time out', 'TIMEOUT']
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
    #Can also have assist on previous play - switching to allow either possibility to result in UNNEC
    #also adding buffer to time allowance because a GOOD 3-pointer can drain 2-3 seconds from clock

    current_play=game_df['PLAY'][idx]
    curr_time=game_df['TIME'][idx]
    curr_time_split = curr_time.split(':')
    curr_time_int = int(curr_time_split[0]) * 60 + int(curr_time_split[1])


    prev_play='Filler String'
    prev_time = 'Filler String'

    try:
        prev_play = game_df['PLAY'][idx-1]
        prev_time = game_df['TIME'][idx-1]
        prev_time_split = prev_time.split(':')
        prev_time_int = int(prev_time_split[0]) * 60 + int(prev_time_split[1])
        
        time_between = prev_time_int-curr_time_int

    #We encounter this exception when the first play of the game is a foul. In STARTING STATE logic,
        #we assume every first foul is a defensive one, so doing the same here
    except KeyError:
        return 'UNNEC'

    #time between <= 3 was causing problems - try replacing with 2
    if (('GOOD' in prev_play)|('Assist' in prev_play)) & (time_between<=1):
        new_state = 'UNNEC'

    #sadly, we need to account for subs and timeouts in between foul and FTs
        
    else:
        play_iterator=1
        valid_play = False
        while not valid_play:
            try:
                #if we encounter a key error here, that means the game ended on this foul
                next_play = game_df['PLAY'][idx+play_iterator]
            except KeyError:
                if team_A in current_play:
                    return 'Bi0'
                elif team_B in current_play:
                    return 'Ai0'
            #otherwise, check next play
                

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
        try:
            next_play = game_df['PLAY'][idx+play_iterator]
        #if KEYERROR - it is likely last play of game, just return opposite team inbound
        except KeyError:
            if team_A in current_play:
                new_state = 'Bi1'
            else:
                new_state = 'Ai1'
            return new_state
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

    try:
        next_play = game_df['PLAY'][idx+1]
        next_time = game_df['TIME'][idx+1]
    except Exception:
        if team_A in current_play:
            new_state = 'Bi{}'.format(str(pv))
        elif team_B in current_play:
            new_state = 'Ai{}'.format(str(pv))
        return new_state

    current_time_split = current_time.split(':')
    next_time_split = next_time.split(':')

    current_time_int = int(current_time_split[0])*60 + int(current_time_split[1])
    next_time_int = int(next_time_split[0])*60 + int(next_time_split[1])

    time_between = current_time_int-next_time_int
    
    #check next play for foul
    #maybe use PV as upper limit for time_between? 3-pointer can hang in the air up to three seconds?
    #or new function to map 2 to 1 and 3 to 3
    if ('Foul' in next_play) & (time_between <= 1):
        if team_A in current_play:
            new_state = 'Af{}'.format(str(pv))
        else:
            new_state = 'Bf{}'.format(str(pv))
    #### IF ASSIST, NEED TO CHECK FOLLOWING PLAY
    elif ('Assist' in next_play) & (time_between == 0):

        #check folloing play for foul
        #if KEYERROR - it is likely last play of game, just return opposite team inbound
        try:
            following_play=game_df['PLAY'][idx+2]
        except KeyError:
            if team_A in current_play:
                new_state = 'Bi{}'.format(str(pv))
            else:
                new_state = 'Ai{}'.format(str(pv))
            return new_state


        if 'Foul' in following_play:

            #measure time of following play
            following_time=game_df['TIME'][idx+2]
            following_time_split=following_time.split(':')
            following_time_int = int(following_time_split[0])*60 + int(following_time_split[1])
            time_between_2 = current_time_int-following_time_int

            #check if foul is associated with GOOD shot - hopefully 1 second gap is right
            if time_between_2 <= 1:
                if team_A in current_play:
                    new_state = 'Af{}'.format(str(pv))
                else:
                    new_state = 'Bf{}'.format(str(pv))

#THIS SECTION REPEATS LOGIC - FUTURE CLEANUP
            #if foul not associated, it's a regular "good" shot
            else:
                if team_A in current_play:
                    new_state = 'Bi{}'.format(str(pv))
                else:
                    new_state = 'Ai{}'.format(str(pv))
        else:
            if team_A in current_play:
                new_state = 'Bi{}'.format(str(pv))
            else:
                new_state = 'Ai{}'.format(str(pv))

    #if no assist or foul, it is a regular "good" shot
    else:
        if team_A in current_play:
            new_state = 'Bi{}'.format(str(pv))
        else:
            new_state = 'Ai{}'.format(str(pv))
#END REPEAT LOGIC SECTION
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