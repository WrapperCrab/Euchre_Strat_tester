from random import shuffle, seed, randrange
import copy

SUITS = ['s','h','d','c']
VALUES = ['9','T','J','Q','K','A']

class Game:
    def __init__(self, players):#players is an array of player instances
        if len(players) != 4:
            raise IllegalPlayException("Game only supports 4 players")
        self.players = players #constant for entire existence
        self.dealerIndex = 3 #index of the dealer in _players. Changes each hand
        self.playersOrder = copy.copy(self.players)#shallow copy of players that can be rotated

        #set positions and teams
        self.teams = [[],[]]
        self._hands = {p: [] for p in self.playersOrder}
        self.inactives = [] #current inactive players for the hand. Only nonempty when going alone
        for p in self.playersOrder:
            p.game = self
            if p == self.playersOrder[0] or p==self.playersOrder[2]:
                p.teamNum = 1
                self.teams[0].append(p)
            else:
                p.teamNum = 2
                self.teams[1].append(p)
        self.gameScore = {1:0,2:0}#current score of the game
        self.tricksScore = {1:0,2:0}#current score of a hand
        self._deck = None
        self.topCard = None
        self.trump = None
        self.caller = None
        self.dealer = None
        self.tricks = []#stores trick data for current hand. array of arrays of cards
        self.playersInTricks = []#stores players that played each card. Lines up with self.tricks

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
            #team 1 won (p1 and p3)
            return 1
        #team 2 won (p2 and p4)
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
            self.tricks.append(trick)
            playersInTrick = []
            self.playersInTricks.append(playersInTrick)
            ledSuit = None
            for playerIndex in range(4):
                p = self.playersOrder[playerIndex]
                if p in self.inactives:
                    continue
                card = p.play(trick,playersInTrick)
                #find led suit
                if len(trick)==0:
                    #this is the first card in the trick
                    ledSuit = self.get_suit(card,self.trump)
                #check for illegal play
                playedSuit = self.get_suit(card,self.trump)
                if (playedSuit!=ledSuit) and (self.has_suit(self._hands[p],self.trump,ledSuit)):
                    raise IllegalPlayException("Must play the led suit if you have it")
                if card not in self._hands[p]:
                    raise IllegalPlayException("player does not have that card to play")
                #add this card to the trick
                trick.append(card)
                playersInTrick.append(p)
                self._hands[p].remove(card)

            winningCard = self.best_card(trick,self.trump,ledSuit)
            winningPlayer = playersInTrick[trick.index(winningCard)]
            self.tricksScore[self.team_num_for(winningPlayer)]+=1

            self._rotate_until_first(winningPlayer)
            if printOutput:
                print(winningPlayer.name,winningCard,trick)
        #score
        self.score_hand()
        #reset
        self.trump = None
        self.top_card = None
        self.inactives = []
        self.dealer = None
        self.caller = None
        self.tricksScore[1] = 0
        self.tricksScore[2] = 0
        self.tricks = []
        self.playersInTricks = []
        for p in self.playersOrder:
            self._hands[p] = []
            p.active = True
    def deal_hand(self):
        self._deck = [value + suit for value in VALUES for suit in SUITS]
        shuffle(self._deck)
        parityDeal = 0
        #Even in code, we must deal correctly! 32322323
        for index in range(4):
            p=self.playersOrder[index]
            cardsToDeal = 0
            if parityDeal%2==0:
                cardsToDeal = 3
            else:
                cardsToDeal = 2
            parityDeal+=1
            for _ in range(cardsToDeal):
                card = self._deck.pop()
                self._hands[p].append(card)
        for index in range(4):
            p = self.playersOrder[index]
            for _ in range(5 - len(self._hands[p])):
                card = self._deck.pop()
                self._hands[p].append(card)
        self.topCard = self._deck.pop()
    def call_trump(self,printOutput):
        if printOutput:
            print("top card", self.topCard)
        #first round of bidding
        for index in range(4):
            p=self.playersOrder[index]
            callResult = p.call(self.topCard)#True, False, or "alone"
            if callResult == False:
                continue
            #the suit has been called
            self.trump = self.topCard[1]
            self._hands[self.dealer].append(self.topCard)
            discard = self.dealer.discard()
            self._hands[self.dealer].remove(discard)
            goingAlone = False
            if callResult == "alone":
                #make the partner inactive
                goingAlone = True
                self.inactives.append(self.teammate_for(p))
                self.teammate_for(p).active = False
                if self.playersOrder[0]==self.teammate_for(p):
                    #The inactive player is first, rotate
                    #This implements left of the dealer rules
                    self._rotate()
                if printOutput:
                    print(p.name, ":",self.trump," Alone!")
            else:
                if printOutput:
                    print(p.name,":",self.trump)
            self.caller = p
            return
        if printOutput:
            print("top card flipped over")
        #second round of bidding
        for playerIndex in range(4):
            p=self.playersOrder[playerIndex]
            call = p.call2(self.topCard)
            if call[1]==False:
                #they passed
                if p==self.dealer:
                    raise IllegalPlayException("The dealer go screwed but didn't call a suit")
                #this is a legal pass
                if printOutput:
                    print(p.name,":",self.trump)
            else:
                #they called
                callResult = call[0]
                if callResult == self.topCard[1]:
                    raise IllegalPlayException("Can't call the face up card after it's flipped")
                self.trump = callResult
                self.caller = p
                goingAlone = False
                if call[1]=="alone":
                    # make the partner inactive
                    goingAlong = True
                    self.inactives.append(self.treammate_for(p))
                    self.teammate_for(p).active = False
                    if self.playersOrder[0]==self.teammate_for(p):
                        #The inactive player is first. rotate
                        #This implements left of the dealer rules
                        self._rotate()
                    if printOutput:
                        print(p.name,":",self.trump," Alone!")
                else:
                    #they did not go alone
                    if printOutput:
                        print(p.name,":",self.trump)
                return

    def score_hand(self):
        callingTeamNum = self.team_num_for(self.caller)
        nonCallingTeamNum = (callingTeamNum%2)+1
        callingTeam = self.teams[callingTeamNum-1]
        nonCallingTeam = self.teams[nonCallingTeamNum-1]
        if self.tricksScore[callingTeamNum]>self.tricksScore[nonCallingTeamNum]:
            #calling team won
            if self.tricksScore[callingTeamNum] == 5:
                #calling team got all 5
                if (callingTeam[0] in self.inactives) or (callingTeam[1] in self.inactives):
                    #calling team made a loner
                    self.gameScore[callingTeamNum]+=4
                else:
                    #calling team did not go alone
                    self.gameScore[callingTeamNum]+=2
            else:
                #Calling team did not get all 5
                self.gameScore[callingTeamNum]+=1
        else:
            #calling team lost
            self.gameScore[nonCallingTeamNum]+=2
    def print_hand(self):
        #print the hand of each player
        print("------------------- Trump:", self.trump, "---------------")
        for index in range(4):
            p = self.playersOrder[index]
            if p not in self.inactives:
                print(self.position_for(p),p.name,self._hands[p])
            else:
                print(self.position_for(p),p.name,"*** asleep ***")

    def hand_for(self,player):
        #returns the hand of player
        return self._hands[player]
    def team_num_for(self,player):
        #return the team number of player
        if player in self.teams[0]:
            return 1
        elif player in self.teams[1]:
            return 2
        else:
            raise Exception("You are not in this game!!??")
    def position_for(self,player):
        #returns the position of player in players list with respect to dealer as position 3
        playerPosition = 0
        for playerIndex in range(4):
            if self.players[playerIndex]==player:
                playerPosition = playerIndex
                break
        return ((3+(playerPosition-self.dealerIndex))%4)
    def teammate_for(self,player):
        #return the teammate of player
        for playerIndex in range(4):
            if (self.playersOrder[playerIndex]==player):
                return self.playersOrder[(playerIndex+2)%4]
    def is_player_active(self,player):
        if player in self.inactives:
            return False
        return True

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
            elif (trump == self.next_suit(card[1])) and (card[0]=='J'):
                #this is the left
                score+=30
            else:
                #this is not trump
                if led==card[1]:
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
    def has_suit(self,cards,trump,suit):
        #returns true if a card of suit suit is in cards
        for card in cards:
            cardSuit = self.get_suit(card,trump)
            if cardSuit == suit:
                return True
        return False

    def _rotate_until_dealer(self,dealerIndex):
        while self.playersOrder[3]!=self.players[dealerIndex]:
            self._rotate()
    def _rotate(self):
        self.playersOrder = self.playersOrder[1:] + self.playersOrder[:1]
    def _rotate_until_first(self,winner):
        #called after a player wins a trick
        while self.playersOrder[0]!=winner:
            self._rotate()

class IllegalPlayException(Exception):
    pass
