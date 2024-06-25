# Euchre Strat Tester

This program simulates Euchre games played by Players with predefined behavior.
You can create your own Players that call and play however you program them to. 

The original code for this concept came from https://github.com/pgwhalen/euchre_sim/. 
A while ago, I forked this repo and added several needed features and fixed a few mistakes. 
I decided to clean up the code, and update it to Python 3, which is the main purpose of this repo.

Try it out and have fun trying to find good strategies, I know I've had fun doing just that.


## The Three Main Classes
This Project has 3 classes: Game (game.py), Player (player.py), and Main (main.py)

Game defines the Euchre game behavior. It stores all information about an ongoing game including what cards are in each players' hands, the score, who is dealer, etc.\
For just testing different strategies, you probably don't need to do anything to game.py unless you want to change the game rules.

Player is where the behavior by each player is stored. What card to play, what trump to call, and what to discard are all decided here.\
The default code in player.py simulates a player with the simplest strategy possible that follows the rules of the game.\
For testing strategies, you should create a new file, say player1.py, which stores a class that inherits Player. \
Then you can override the relevant functions to get your wanted behavior.

Main is where the players and game are initialized.\
One thing you could do is run thousands of games between teams of players with different strategies,
then do statistical analysis to determine if one strategy performs well against the other.\
Or you could just set it to play one game and read the output. Pick your poison.


## How to Create a Player
To create a player with your own behavior, you should create a script, say player1.py which contains a class that inherits Player.\
Player has 4 important functions that you may want to override when creating your own player.\
Read farther down to see how to access Game data such as the score, what position this player is in, and of course, their hand.

### Functions
These functions are all automatically called with the correct parameters by Game for each player at the correct part of the game.
1. `play(trick,playersInTrick)`\
This function defines your player's behavior when it is their turn to play a card.\
Output must be a card currently in this player's hand that follows suit.

3. `call(topCard)`\
This function defines your player's behavior during the first round of bidding.\
Output must be one of:
    1. `True` for calling
    2. `False` for passing
    3. `"alone"` for calling trump alone

4. `call2(topCard)`\
This function defines your player's behavior during the second round of bidding.\
Output must be an array of size 2 that contains `[the suit you are calling`,`True for calling, False for passing, or "alone" for going alone]`\
The suit is just a character denoting the wanted suit. Must be one of `'s','h','d','c'`\
If the second element is False, then the first element is ignored, but it must be present.\
Output must also follow the rules of play. 
    1. The suit of the top card cannot be called 
    2. Stick the Dealer is implemented, so the dealer cannot pass in this round.

5. `discard()`\
This function defines your player's behavior when they are dealer and it is time for them to discard one card from their hand.\
Output must be a card currently in this player's hand.

### Accessing Game Data
Nothing is stored in Player other than their name and their game (the Game instance they are part of). Players do not even store their own hand of cards.
The Game that this player is a part of stores all of that, so you will have to get all information from Game.\
Heres how to get some commonly desired values:
1. This Player's hand\
call `self.game.hand_for(self)`.\
This returns an array with this player's current hand.
3. The turned up card\
`self.game.topCard`.\
topCard is also often a parameter of Player functions, so you could alternatively just use `topCard`.
4. Trump\
`self.game.trump`\
returns the trump suit, so a character like `'s'`
10. This Player's Position\
`self.game.position_for(self)`\
returns a number 0 to 3 where 3 is dealer
11. This Player's Team Number\
`self.game.team_num_for(self)`\
returns 1 or 2 depending on what team this player is on
12. This Player's active status\
`self.game.is_player_active(player)`\
returns Falso only if the given player is inactive due to their partner going alone.
13. the game score\
`self.game.gameScore`\
returns a dictionary which maps each team number (1 and 2) to their score
14. The trick score\
`self.game.tricksScore`\
returns a dictionary which maps each team number (1 and 2) to their score
16. All cards played in this hand so far\
`self.game.tricks`\
returns an array of arrays of cards. Each array is four cards in the order that they were played in one trick. Includes the cards of the current trick as well\
In order to get the players that played each of these cards, use `self.game.playersInTricks`.
This returns an array of arrays of players that lines up with tricks.

For example, if Steve is at playersInTricks[0][2], then that means Steve was the (2+1)th player in the (0+1)th trick and played the card tricks[0][2]

This is not an exhaustive list. Check the values set in `__init__` for game.py as well as the functions to be called by Players for more.

## A Guide to Statistical Testing
My favorite use case for this project is to do statistical testing on different Euchre strategies. I'll briefly go over how I've gone about it here.

Let's say you have 2 strategies: Player1 and Player2, and you want to know if Player2 is significantly better than Player1. How can we tell?\
The statistically sound way to go about this is to have a Control group and an Experimental group.

To do this, create 8 players like so:
```
#control game
#team 1
p1 = Player1("Henry")
p3 = Player1("Paul")
#team 2
p2 = Player1("Alex")
p4 = Player1("Sarah")

#experimental game
#team 1a
p1a = Player2("HenryA")
p3a = Player2("PaulA")
#team 2a
p2a = Player1("AlexA")
p4a = Player1("SarahA")
```
Now we will have each set of teams face the same randomly generated games. 
If team 1a has a significantly better win rate than team 1, we can say with confidence that Player2 strategy 'beats' the Player1 strategy.

To play the games, do something like this:
```
numGames = 1#Number of games played
neededScore = 1#Number of points needed to win a game
printOutput = True#Whether or not each hand is printed in the console

for index in range(numGames):
    randSeed = randrange(-10000,10000)

 		gControl = Game([p1a, p2a, p3a, p4a])
 		team1aScore+=gControl.play_game(neededScore, randSeed, printOutput)

 		gTest = Game([p1, p2, p3, p4])
 		team1Score+=gTest.play_game(neededScore, randSeed, printOutput)

print "team 1 won ",team1Score," games out of ", numGames
print "team 1a won ",team1aScore," games out of ", numGames
```

Then, just run a proportions test on the results. 
I don't have any built in methods to do this because I just do in on my TI-nspire CX CAS calculator which has a very reasonable short name.

## Game Rules
The way game.py is written implements some basic rules that you may be interested in changing
1. Left of the Dealer and Stick the Dealer are implemented in the `call_trump()` function in game.py
2. Farmer's hands are not implemented at all.
3. All players must follow the rules or the game will stop with an error. No reneging or stealing the deal
    1. Although, not much is stopping you from programming a player that knows the cards in other players' hands


## Other Things
1. `Note:` A 'card' is just a 2-character string. The card value `'9','T','J','Q','K','A'` and the suit `'s','h','d','c'`.
See the deck of cards created in one line at the beginning of the `deal_hand()` function in game.py
