from random import shuffle, seed, randrange
import copy

SUITS = ['s','h','d','c']
VALUES = ['9','T','J','Q','K','A']

class Game:
    def _init_(self, players):#players is an array of player instances
        if len(players) != 4:
            raise IllegalPlayException("Game only supports 4 players")
        self.players = players #constant for entire existence
        self.dealerIndex = 3 #index of the dealer in _players. Changes each hand
        self.playersOrder = copy.copy(self._players)#shallow copy of players that can be rotated

        #set positions and teams
        self.teams = [[],[]]
        self._hands = {p: [] for p in self.playersOrder}
        self.inactives = [] #current inactive players for the hand. Only nonempty when going alone
        for p in self.playersOrder:
            p.game = self
            if p == self.PlayersOrder[0] or p==self.playersOrder[2]:
                p.teamNum = 1
                self._teams[0].append(p)
            else:
                p.teamNum = 2
                self._teams[1].append(p)
        self.gameScore = {1:0,2:0}#current score of the game
        self.tricksScore = {1:0,2:0}#current score of a hand
        self._deck = None
        self.topCard = None
        self.trump = None
        self.caller = None
        self.dealer = None

    def play_game(self,neededScore,randSeed,printOutput):
        seed(randSeed)
        #select a random dealer
        self.dealerIndex = randrange(4)
        while (self.gameScore[1] < neededScore and self.gameScore[2]<neededScore):
            self.dealerIndex = (self.dealerIndex+1)%4#go to the next dealer
            self.play_hand(printOutput)
            if printOutput:
                print("===============> SCORE:",self.gameScore)
        if printOutput:
            print("GAME OVER!")
        #return value indicating which team won
        if self.gameScore[1]>=neededScore:
            return 1
        return 0

    def play_hand(self,printOutput):
        self._rotate_until_dealer(self.dealerIndex)
        self.dealer = self.playersOrder[3]
        #deal
        self.deal_hand()
        #call trump
        self.call_trump(printOutput)
        if printOutput:
            self.print_hand()
        #play tricks
        for _ in range(5):
            trick = []
            playersInTrick = []
            ledSuit = None
            for playerIndex in range(4):
                p = self.playersOrder[playerIndex]
                if p in self.inactives:
                    continue
                card = p.play(trick,playersInTrick)
                #find led suit
                if len(trick)==0:
                    #this is the first card in the trick
                    ledSuit = self.get_card_suit(card,self.trump)
                #check for illegal play
                playedSuit = self.get_card_suit(card,self.trump)
                if playedSuit!=ledSuit:
                    raise IllegalPlayException("Must play the led suit if you have it")
                if card not in self._hands[p]:
                    raise IllegalPlayException("player does not have that card to play")
                #add this card to the trick
                trick.append(card)
                playersInTrick.append(p)
                self._hands[p].remove(card)
            winningCard = self.best_card(trick,self.trump,ledSuit)



    def hand_for(self,player):
        #returns the hand of player
        return self._hands[player]

    def get_suit(self,card,trump):
        if (card[0]=='J') and (card[1]==self.next_suit(trump)):
            #this is the left
            return trump
        return card[1]
    def next_suit(self,suit):
        match suit:
            case 's':
                return 'c'
            case 'h':
                return 'd'
            case 'c':
                return 's'
            case 'd':
                return 'h'

    def best_card(self,cards,trump=None,led=None):
        #returns the winning card from cards given trump and led suits
        #correct even if trump and or led are None
        bestCard = None
        bestCardScore = 0
        for card in cards:
            score = 0
            if trump == card[1]:
                if card[0] == 'J':
                    #this is the right
                    score+=40
                else:
                    score+=20
            elif (trump == next_suit(card[1])) and (c[0]=='J'):
                #this is the left
                score+=30
            else:
                #this is not trump
                if led==c[1]:
                    #this is led suit
                    score+=10
                else:
                    #this card is not special
                    pass
            #add value for face value
            match card[0]:
                case 'A':
                    score+=6
                case 'K':
                    score+=5
                case 'Q':
                    score+=4
                case 'J':
                    score+=3
                case 'T':
                    score+=2
                case '9':
                    score+=1
            #Check if this is the best card so far
            if score>bestCardScore:
                bestCard = card
                bestCardScore = score
        return bestCard


    def _rotate_until_dealer(self,dealerIndex):
        while self.playersOrder[3]!=self._players[dealerIndex]:
            self._rotate()
    def _rotate(self):
        self.playersOrder = self.playersOrder[1:] + self.playersOrder[:1]
    def _rotate_until_first(self,winner):
        #called after a player wins a trick
        while self.playersOrder[0]!=winner:
            self._rotate()

class IllegalPlayException(Exception):
    pass