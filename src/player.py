from card import Card

import calendar
import time


class Player:
    def __init__(self, name, chips=1000) -> None:
        self.name = name
        self.cards = []
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
    
    def getCards(self) -> [Card]:
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
        self.cards = []