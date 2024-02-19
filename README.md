"# NCAA_Markov" 

Roadmap
Find data endpoint for play-by-play and roster

Write functions to pull and process those data

Create very small markov model on one game without player data, just time and scores

run simulation of game with that model

add starting player data and repeat

pull multiple games in the order of 10-100 and train the model on that

create matchup that did not exist in training data and simulate that

write functions to process the possibility of player substitutions




NOTES
2/16/2024
The logic written out in translate_game was applied to the first sample game

It was refined using second sample game and moved into game_states_logic.py
Shortcomings still exist which are we don't have a starting state and we don't have auto-detect team A and team B

Going to open a new notebook to test a third sample game and add logic to detect starting state and auto detect team A and team B
During this time, will also add pulling game logic to a PY file so we can pull and test game in same notebook

Third game worked without a hitch - labeled manually and then ran logic and all matched (except on plays where Foul is followed by Turnover at same timestamp, where logic says it's Bi0 then Br0. That's fine, just leave it)

NOTES 2/18/2024
Don't use:
#UTRVG? 506558?
#North American? 536?
#Army West Point vs ANY
#NC A&T vs T
#Vanguard 30135
#Wittenburg FW
#Navajo Tech 506563
#Bob Jones XXXXXX
#Texas A&M is M?
#Warren Wilson 30236
#Carolina Christian 506565
#stanton 506567
#edward waters 30244
#new college FL - 506568
#UNT Dallas 506547
#Coker USCU?
#error with game 6198622
