from game import Game
from player import Player


from random import randrange

def main():
    p1 = Player("Henry")
    p3 = Player("Paul")

    p2 = Player("Alex")
    p4 = Player("Sarah")

    team1Score = 0 #number of games p1 and p3 won

    numGames = 1 #number of games to be played
    neededScore = 10 #number of points to win a game
    printOutput = True #is each hand printed in the console
    for index in range(numGames):
        randSeed = randrange(-100000,100000)
        game = Game([p1,p2,p3,p4])
        team1Score += game.play_game(neededScore,randSeed,printOutput)

    print("team 1 won ",team1Score," games out of ",numGames)

if __name__=='__main__':
    main()