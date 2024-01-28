

class Player:
    def _init_(self,name):
        self.name = name
        self.game = None

    def play(self,trick,playersInTrick):
        #return a card to play in the trick. DON'T RENEGE
        if len(trick) == 0:
            #we are first
            return self.game.hand_for(self)[0]
        #we are not first, try to follow suit
        ledSuit = self.game.get_suit(trick[0],self.game.trump)
        for card in self.game.hand_for(self):
            cardSuit = self.game.get_suit(card,self.game.trump)
            if (cardSuit == ledSuit):
                return card
        #we don't have any of the led suit
        return self.game.hand_for(self)[0]

    def call(self, topCard):
        #first round of bidding
        #return true to pickup or false to pass or "alone" to go alone
        return True

    def call2(self,topCard):
        #second round of bidding
        #return suit and alone call like so: [suit,True/False/"alone"]
        #suit is disregarded if False is returned
        if topCard[1]=='d':
            return ['s',True]
        return ['d',"alone"]

    def discard(self):
        #choose a card from your hand to get rid of after picking up
        return self.game.hand_for(self)[0]




