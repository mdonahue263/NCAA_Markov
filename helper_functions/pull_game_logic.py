import requests
import json
import pandas as pd

def pull_game(game_id):
    """
    Use Requests to hit hidden API endpoint on NCAA for play-by-play
    Args:
        game_id: INT or STR, 7 digits as far as I can tell
        smallest seems to be 6197002, starting this season
        6196001 seems to still be D1 mens bball but in the future??
        Need to see what happens when we try to ping A) future games and B)non basketball
        6195001 is a hockey game, see what happens there
        Ice Hockey is mentioned in ['meta']['title'], but basketball does not do that
        Trying soccer - 6191603
        Same conclusion with soccer. This will be annoying but might be worth checking if all other sports do that
        No - lacross has exact same title as bball. We can get past this by checking all the text for a buzzword
        
        
    
    """
    global r
    url = "https://data.ncaa.com/casablanca/game/{}/pbp.json".format(str(game_id))
    r = requests.get(url)
    #check if "Layup" exists in the content otherwise fail
    cont = r.content
    
    if ('Layup' not in str(cont)) and ('layup' not in str(cont)) and ('LAYUP' not in str(cont)):
        raise Exception('This may be the wrong sport')
    
    
    
    json_copy = json.loads(r.content)
    
    if json_copy == {'Message': 'Object not found.'}:
        raise Exception("Invalid game_id or future game_id")
    
    #pull date
    date=json_copy['updatedTimestamp']
    
    #pull data from json object
    meta_info = json_copy['meta']['teams']

    team1 = [meta_info[0]['homeTeam'],meta_info[0]['id'],meta_info[0]['shortName']]
    team2 = [meta_info[1]['homeTeam'],meta_info[1]['id'],meta_info[1]['shortName']]

    team_data = pd.DataFrame([team1,team2],columns=['home','id','name'])

    game=json_copy['periods']
    
    #don't yet know how to handle overtime
    if len(game) != 2:
        raise ValueError
    
    first_half=game[0]
    second_half=game[1]
    
    #Initialize empty dataframe
    box_score=pd.DataFrame()
    
    #scores will be 0 until scoring_started is True
    scoring_started=False
    
    #iterate through first_half states
    for item in first_half['playStats']:
        score=item['score']
        time=item['time']
        v_text=item['visitorText']
        h_text=item['homeText']

        if len(h_text) == 0:
            all_text = v_text
        else:
            all_text = h_text
        
        #if score field is blank, either 0-0 or same as previous score
        if (len(score) == 0):
            if (scoring_started==False):
                home_score=0
                away_score=0
            else:
                #no code necessary here but for show:
                home_score=home_score
                away_score=away_score
                
        #otherwise, it is in the format "AWAY-HOME"
        elif len(score) != 0:
            scoring_started=True
            away_score, home_score = score.split('-')
            away_score=int(away_score)
            home_score=int(home_score)
            
        half=1

        #create row for state
        current_state = pd.DataFrame({'Period':half,
                                      'TIME':time,
                                       'Away':away_score,
                                      'Home':home_score,
                                  'PLAY':all_text},index=[0])
        box_score=pd.concat([box_score,current_state])
        
        #same iterations but no need for "first Score" logic
    for item in second_half['playStats']:
        score=item['score']
        time=item['time']
        v_text=item['visitorText']
        h_text=item['homeText']
        if len(score) == 0:
                home_score=home_score
                away_score=away_score
        else:
            scoring_started=True
            away_score, home_score = score.split('-')
            away_score=int(away_score)
            home_score=int(home_score)

        if len(h_text) == 0:
            all_text = v_text
        else:
            all_text = h_text
            
        half=2

        current_state = pd.DataFrame({'Period':half,
                                      'TIME':time,
                                       'Away':away_score,
                                      'Home':home_score,
                                  'PLAY':all_text},index=[0])
        box_score=pd.concat([box_score,current_state])
        
        
    box_score=box_score.reset_index(drop=True)
    return {'data': box_score, 'teams': team_data}