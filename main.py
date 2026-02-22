import random
import copy

from game import Game
from player import Player
from gamestate import Gamestate


from random import randrange

def main():
    testState = Gamestate(
        'call', ['9','c'], 0, 
        [
            [['9','h'], ['A','d'], ['9','d'], ['T','s'], ['K','h']],
            [['Q','s'], ['J','s'], ['K','d'], ['A','h'], ['A','s']],
            [['T','d'], ['T','c'], ['K','s'], ['J','d'], ['Q','c']],
            [['Q','d'], ['A','c'], ['9','s'], ['Q','h'], ['J','c']]
        ], 
        [['9','c'], ['T','h'], ['J','h'], ['K','c']], None, 
        [0,0], [], [], 
        False, 0, '_'
    )

    random.shuffle(testState.hands[0])
    random.shuffle(testState.hands[1])
    random.shuffle(testState.hands[2])
    random.shuffle(testState.hands[3])

    testState.find_value()
    testState.print_verbose()
    tempState = copy.copy(testState)
    while True:
        if tempState.bestChild != None:
            tempState = copy.copy(tempState.bestChild)
            tempState.print_verbose()
        else:
            break
        
    # Travel down the optimal trajectory
    # trajectory = testState.bestTrajectory
    # for moveIndex in trajectory:
    #     testState = testState.create_child_from_move(int(moveIndex))
    #     testState.print_verbose()

if __name__=='__main__':
    main()

    # [['',''], ['',''], ['',''], ['',''], ['','']],
    # [['',''], ['',''], ['',''], ['',''], ['','']],
    # [['',''], ['',''], ['',''], ['',''], ['','']],
    # [['',''], ['',''], ['',''], ['',''], ['','']]

    # Variations of this are interesting. In this one, it takes forever to calculate and the optimal strat has 1st pass
    # and let the partner call it. On this hand! Lol!
    # Takes ungodly long for topcard 9h. It's clear we need to add some speedup strategies
    # testState = Gamestate(
    #     'call', ['9','s'], 0, 
    #     [
    #         [['J','s'], ['A','s'], ['K','s'], ['Q','s'], ['T','s']],
    #         [['J','c'], ['A','c'], ['K','c'], ['Q','c'], ['T','c']],
    #         [['J','h'], ['A','h'], ['K','h'], ['Q','h'], ['T','h']],
    #         [['J','d'], ['A','d'], ['K','d'], ['Q','d'], ['T','d']]
    #     ], 
    #     [['9','d'], ['9','s'], ['9','c'], ['9','h']], None, 
    #     [0,0], [], [], 
    #     False, 0, '_'
    # )

    # Runs ultra quick! Guess picking it up was a bad idea!
    # testState = Gamestate(
    #     'discard', ['A','s'], 3, 
    #     [
    #         [['A','d'], ['J','c'], ['T','h'], ['T','d'], ['J','s']],
    #         [['J','d'], ['A','c'], ['K','h'], ['T','s'], ['Q','h']],
    #         [['9','d'], ['K','c'], ['9','s'], ['T','c'], ['K','s']],
    #         [['K','d'], ['Q','c'], ['9','h'], ['J','h'], ['Q','s'], ['A','s']]
    #     ], 
    #     [], [3, 's', False], 
    #     [0,0], [], [], 
    #     False, 0, '_'
    # )


    # testState = Gamestate(
    #     'play', ['J','h'], 0, 
    #     [
    #         [['K','d'], ['Q','h'], ['9','d'], ['9','h'], ['A','h']], 
    #         [['A','d'], ['Q','c'], ['T','d'], ['J', 'd'], ['J','c']],
    #         [['K','h'], ['A','c'], ['9','c'], ['T', 's'], ['K','c']],
    #         [['9','s'], ['T','h'], ['J','h'], ['A', 's'], ['K','s']]
    #     ], 
    #     [], [3, 'h', False], 
    #     [0,0], [], [], 
    #     False, 0, '_'
    # )