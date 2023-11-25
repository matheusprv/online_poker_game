from card import Card

import calendar
import time


class Player:
    def __init__(self, name, chips=1000) -> None:
        self.name = name
        self.cards = []
        self.selectedCommunityCards = []
        self.cardsPoints = 0
        self.chips = chips
        self.wins = 0
        self.defeats = 0

        currentGMT = time.gmtime()
        timeStamp = calendar.timegm(currentGMT)
        self.id = str(timeStamp) + name

    def setActive(self, active) -> None:
        self.active = active

    def getActive(self) -> bool:
        return self.active
    
    # 1: small blind, 2: big blind, 3: normal
    def setFunction(self, gameFunction) -> None:
        self.gameFunction = gameFunction
    
    def getFunction(self) -> int:
        return self.gameFunction
    
    def incrementWins(self) -> None:
        self.wins += 1

    def incrementDefeats(self) -> None:
        self.defeats += 1

    def getWins(self) -> int:
        return self.wins

    def getDefeats(self) -> int:
        return self.defeats
    
    def setCards(self, cards) -> None:
        self.cards = cards
    
    def getCards(self) -> list[Card]:
        return self.cards

    def getName(self) -> str:
        return self.name

    def bet(self, value) -> None:
        self.chips -= value

    def setChips(self, chips) -> None:
        self.chips = chips

    def resetPlayer(self) -> None:
        self.wins = 0
        self.defeats = 0
        self.cardsPoints = 0
        self.cards = []
        self.selectedCommunityCards = []

    def sortCards(self, cards) -> list[Card]:
        return sorted(cards, key = lambda card : card.getWeight())


    def checkSameKind(self, cards) -> bool:        
        kind = cards[0].getKind()
        for card in cards[1:]:
            if card.getKind() != kind:
                return False
        return True
    

    def checkSequential(self, cards) -> bool:
        #knowing that cards are sorted, we know if they are sequential if the last weight is equal to the first +4
        idealLastWeight = cards[0].getWeight() + 4
        return (cards[-1].getWeight() == idealLastWeight)


    def checkSameValue(self, cards) -> {}:
        #check if we have n cards with the same value
        countSameValues = {}
        
        for card in cards:
            countSameValues.setdefault(card.value, 0)
            countSameValues[card.value]+=1

        return countSameValues


    def countCardsPoints(self) -> int:

        cards = self.cards + self.selectedCommunityCards        
        points = sum(card.getWeight() for card in cards)

        cards = self.sortCards(cards)

        if(self.checkSameKind(cards)):
            if(self.checkSequential(cards)):
                if(cards[4].getWeight() == 14):
                    #royal flush
                    points += 1000
                else:
                    #straight flush
                    points += 900
            else:
                #flush
                points += 600
        
        elif self.checkSequential(cards):
            # straight
            points +=500

        else:
            countSameValues = self.checkSameValue(cards)
            maxSameValues = max(countSameValues.values())

            if(maxSameValues == 4):
                #four of a kind
                points += 800
            
            elif(maxSameValues == 3):
                if(2 in countSameValues.values()):
                    #full house
                    points += 700

                else:
                    #three of a kind
                    points += 400

            elif(maxSameValues == 2):
                if(list(countSameValues.values()).count(2) == 2):
                    #two pair
                    points += 300
                
                else:
                    #one pair
                    points += 200

            else:
                #high card
                points += 100
        
        self.cardsPoints = points
        return points