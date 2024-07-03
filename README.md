This is a project started in 2024 to try to model the flow of NCAA men's basketball games as transitions between states in a Markov Chain-esque way.

The general idea is based on this brief paper https://www.nessis.org/nessis07/Kenny_Shirley.pdf.

The paper describes a model where the states are defined as a combination of 3 things:
1. Which team has possession
2. How that team gained possession
3. The number of points on the previous play

The paper demonstrates a maximum of 40 states, then reduces the number to 30 based on some impossible states. For example, a scoring play cannot result in a "Steal," so a steal can only happen on a 0-point play.

These 30 states are demnstrated visually in the graphic Shirley_30_states.png

In my model, I further simplify the state space by eliminating states that are effectively redundant for the outcome of a game. For example, I eliminate the "Steal" category by considering a "Steal" to be identical to a "Defensive Rebound."

I further reduce the state space by considering "offensive rebounds" and "defensive rebounds" redundant; the information of which team made the rebound is captured by the indication of which team now has possession.

These reductions result in the model I used as the starting point for the project, which has 18 states and can be seen in the graphic Donahue_18_States.png.

After creating this framework with which to describe the events of a game, I chose a single game to test the framework by hand.

To identify what resource I would use for this, I scrolled through various sports data websites to find the most easily accessible play-by-play data, and I found that on NCAA's website. I found that the play-by-play data is available via a "hidden API" endpoint that delivers a simple JSON version of the play-by-play data, so I use that later, but for now, I simply pasted the play-by-play description of a single game into excel. I used the game from 2/7/2024, LSU at Tennessee, which has game ID 6200293 on NCAA's website.

You can see the sample labeling of each play in the excel workbook Outline_and_Sample.xlsx, in the Sample tab. For each line of the play-by-play score, I tried to identify a "Previous State" and a "New State" that each fell into one of the 18 defined states from above. In many cases, the play-by-play line had a description that did not fit any, but was not relevant to the score of the game, so it was labeled "UNNECESSARY" instead of a state. For example, missed shots are followed by rebounds or inbounds, and we do not need a separate state for missed shot and rebound. 

To illustrate the first few lines of the sample game, I labeled Tennessee as team A and LSU as team B. The first play is a "Foul on LSU", followed by a "Free throw Good" by Tennessee. This can be represented as starting with a Tennessee inbound (Ai0), followed by a Tennessee Free Throw after no score (Af0), followed by a Tennessee Free Throw after 1 point (Af1).

I continue labeling the play-by-play data of the first sample game to ensure that the previously defined 18 states would be sufficient to capture the flow of the entire game. After ensuring this was true for a few more games, I began to map out some logic to automatically process the play-by-play data for each game.

For the most simple breakdown of how I approached this logic, see the Rules tab of the Outline_and_Sample.xlsx workbook. Some of the most simple parts of the logic were disregarding all lines where a shot was MISSED, in favor of using the following line's information. This works because a MISS is typically followed by a Rebound or Inbound.

NOTE: This logic is crude and manual and still a work in progress. Accounting for every possible play-by-play line is difficult, and there are many "exceptions" and mislabeled data in practice. This should be a point of focus in future iterations, because this is cause for a lot of bad data (impossible transitions pop up, scores are missed, etc.)

