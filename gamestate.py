import copy

SUITS = ['s','h','d','c']
VALUES = ['9','T','J','Q','K','A']

STAGES = ['call', 'call2', 'discard', 'play']

# This class stores all the needed information for the state of one game
# Additionally, it contains methods for converting this gamestate to the gamestate after the next decision is made


class Gamestate: # Stores all the date for any stage of one hand of euchre (no game score)
    def __init__(self, stage, topCard, playerToGo, 
                 hands, kitty, call, tricksScore, 
                 trick, inactives, handComplete, nestLevel, key):
        # Meta variables
        self.value = 0 #to be changed to the highest point value for the team to move from all child games
        self.bestMove = None
        self.bestTrajectory = '' #Store the key of the game that is valued as the best starting from this state
        self.nestLevel = nestLevel
        self.key = key
        print(key)
        self.bestChild = None #Store an instance of an optimal child state

        # Unchanging variables
        self._dealerIndex = 3 #index of the dealer
        self._teams = [[0,2],[1,3]] #[0, 2] get positive values, [1,3] get negative values
        self.topCard = topCard

        # Stage variables
        self.stage = stage
        self.playerToGo = playerToGo #index of next player to move regardless of game stage
        self.hands = hands #hands[0] is list of cards held by first position, etc
        self.kitty = kitty #contains the topcard until it is picked up. During discard, contains only 3 cards

        self.call = call #[{index of player who called}, {suit}, {true or false alone}]
        self.tricksScore = tricksScore #[numtricks team 0, numtricks team 1]

        self.trick = trick #cards played so far in the trick. Once 4 are played, this data is forgotten
        self.inactives = inactives #[{index of player who's partner is alone}]
        self.handComplete = handComplete #true if the final card has been played

    def find_value(self):
        if self.handComplete:
            self.value = self.score_hand()
            # self.print_summary()
            return self.value

        # look over all children and calculate their value
        moves = self.get_legal_moves()
        count = 0
        for moveIndex in range(len(moves)):
            child = self.create_child_from_move(moveIndex)
            childValue = child.find_value()
            #Only change if this value is better
            if self.value == 0:
                self.value = childValue
                self.bestMove = moves[moveIndex]
                self.bestTrajectory = str(moveIndex) + child.bestTrajectory
                self.bestChild = child
            else:
                if self.playerToGo in self._teams[0]:
                    if childValue > self.value:
                        self.value = childValue
                        self.bestMove = moves[moveIndex]
                        self.bestTrajectory = str(moveIndex) + child.bestTrajectory
                        self.bestChild = child
                else:
                    if childValue < self.value:
                        self.value = childValue
                        self.bestMove = moves[moveIndex]
                        self.bestTrajectory = str(moveIndex) + child.bestTrajectory
                        self.bestChild = child


            #!!!Check if we have reached the best value
            if self.stage == 'play':
                if self.playerToGo in self._teams[0] and self.value == self.get_max_possible_value():
                    return self.value
                elif self.value == self.get_min_possible_value():
                    return self.value
            count += 1
        return self.value

    def get_max_possible_value(self):#!!! Does not account for loners
        # Calculates the highest score differential for team 1 possible given the call and the current trick score
        if self.team_index_for(self.call[0]) == 0:
            #team 1 called
            if self.tricksScore[1] == 0:
                return 2
            elif 1 <= self.tricksScore[1] and self.tricksScore[1] <=2:
                return 1
            else:
                return -2
        else:
            #team 2 called
            if self.tricksScore[1] == 5:
                return -2
            elif 3 <= self.tricksScore[1] and self.tricksScore[1] <= 4:
                return -1
            else:
                return 2
    def get_min_possible_value(self):#!!! Does not account for loners
        #!! Should becombined with get_max_possible_value using sign_team_score
        # Calculates the highest score differential for team 2 possible given the call and the current trick score
        if self.team_index_for(self.call[0]) == 1:
            #team 2 called
            if self.tricksScore[0] == 0:
                return -2
            elif 1 <= self.tricksScore[0] and self.tricksScore[0] <=2:
                return -1
            else:
                return 2
        else:
            #team 1 called
            if self.tricksScore[0] == 5:
                return 2
            elif 3 <= self.tricksScore[0] and self.tricksScore[0] <= 4:
                return 1
            else:
                return -2

    def create_child_from_move(self, moveIndex):# This function assumes the move is legal
        move = self.get_legal_moves()[moveIndex]

        #initialize with current values
        newStage = self.stage
        newTopCard = copy.copy(self.topCard) # Never changes
        newPlayerToGo = self.playerToGo
        newHands = copy.deepcopy(self.hands)
        newKitty = copy.deepcopy(self.kitty)
        newCall = copy.deepcopy(self.call)
        newTricksScore = copy.copy(self.tricksScore)
        newTrick = copy.deepcopy(self.trick)
        newInactives = copy.copy(self.inactives)
        newHandComplete = self.handComplete
        newNestLevel = self.nestLevel + 1
        newKey = self.key + str(moveIndex)

        #calculate changes to state
        match self.stage:
            case 'call': #move is 'pass' 'call' or 'alone'
                match move:
                    case 'pass':
                        if self.playerToGo == 3:
                            newStage = 'call2'
                        newPlayerToGo = (self.playerToGo+1)%4
                    case 'call':
                        newStage = 'discard'
                        newPlayerToGo = 3
                        newHands[3].append(newTopCard)
                        newKitty.remove(newTopCard)
                        newCall = copy.deepcopy([self.playerToGo, newTopCard[1], False])
                    case 'alone':#!!! Leave empty for now
                        pass
            case 'call2':
                if move == 'pass':
                    newPlayerToGo = (self.playerToGo+1)%4
                elif move[1] == False:
                    newStage = 'play'
                    newPlayerToGo = 0
                    newCall = copy.deepcopy([self.playerToGo, move[0], False])
                else: #!!! This is a loner. leave empty for now
                    pass
            case 'discard': #!!! Does not account for loners
                newStage = 'play'
                newPlayerToGo = 0
                newHands[3].remove(move)
                newKitty.append(move)
            case 'play': #!!! Does not account for loners
                trump = self.call[1] #helper
                newTrick.append(move)
                if len(newTrick) == 4:
                    bestCard = self.best_card(newTrick, trump, self.get_suit(newTrick[0], trump))
                    newPlayerToGo = ((newTrick.index(bestCard))+(self.playerToGo+1)%4)%4
                    newHands[self.playerToGo].remove(move)
                    newTricksScore[self.team_index_for(newPlayerToGo)] += 1
                    newTrick = []
                    if len(newHands[0]) == 0:
                        newHandComplete = True
                else:
                    newPlayerToGo = (self.playerToGo+1)%4
                    newHands[self.playerToGo].remove(move)

        #Create the child
        return Gamestate(newStage, newTopCard, newPlayerToGo, newHands, newKitty, newCall, newTricksScore, newTrick, newInactives, newHandComplete, newNestLevel, newKey)




    def print_summary(self):
        print("")
        print("State Summary:")
        print("This state's key is " + str(self.key))
        print("stage is " + self.stage)
        print("state value is " + str(self.value))

        print("")
        print("The player to go is " + str(self.playerToGo))
        print("the set of available moves is " + str(self.get_legal_moves()))
        print("The best move is " + str(self.bestMove))
        print("---------------------------------")
    def print_verbose(self):
        print("")
        print("State Summary Verbose:")
        print("This is nest level " + str(self.nestLevel))
        print("This state's key is " + str(self.key))
        print("stage is " + self.stage)
        print("The best trajectory from this state is " + self.bestTrajectory)
        print("state value is " + str(self.value))

        print("")
        print("The player to go is " + str(self.playerToGo))
        print("the set of available moves is " + str(self.get_legal_moves()))
        print("The best move is " + str(self.bestMove))

        print("")
        print("the top card is " + str(self.topCard))
        print("The hands are " + str(self.hands))
        print("The call is " + str(self.call))
        print("The trick score is " + str(self.tricksScore))
        print("The trick so far is " + str((self.trick)))
        print("The hand is over: " + str(self.handComplete))
        print("---------------------------------")

    def get_legal_moves(self): #!!! No loners for now
        moves = []
        match self.stage:
            case 'call':
                moves.append('pass')
                moves.append('call')
                # moves.append('alone')
            case 'call2':
                turnedSuit = self.topCard[1]
                for suit in SUITS: #!! Does this work?
                    if suit != turnedSuit:
                        moves.append([suit, False])
                        # moves.append([suit, True])
                if self.playerToGo != self._dealerIndex:
                    moves.append('pass')
            case 'discard':
                for card in self.hands[self.playerToGo]:
                    moves.append(card)
            case 'play':
                playerHand = self.hands[self.playerToGo]
                if len(self.trick) == 0:
                    for card in playerHand:
                        moves.append(card)
                else:
                    ledCard = self.trick[0]
                    trump = self.call[1]
                    if self.has_suit(playerHand, trump, self.get_suit(ledCard, trump)):
                        for card in playerHand:
                            if self.get_suit(card, trump) == self.get_suit(ledCard, trump):
                                moves.append(card)
                    else:
                        for card in playerHand:
                            moves.append(card)
        return moves

    def score_hand(self):
        callingTeamIndex = self.team_index_for(self.call[0])
        if self.tricksScore[callingTeamIndex] >= 3:
            #calling team made it
            if self.tricksScore[callingTeamIndex] == 5:
                #calling team got all 5
                if (self._teams[callingTeamIndex][0] in self.inactives or self._teams[callingTeamIndex][1] in self.inactives):
                    #made loner
                    return self.sign_team_score(callingTeamIndex, 4)
                return self.sign_team_score(callingTeamIndex, 2)
            return self.sign_team_score(callingTeamIndex, 1)
        else:
            #euchre
            return self.sign_team_score(callingTeamIndex, -2)
    def sign_team_score(self, callingTeamIndex, score):
        if callingTeamIndex == 0:
            return score
        return -score

    def team_index_for(self,player):
        #return the team index of player
        if player in self._teams[0]:
            return 0
        else:
            return 1
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
