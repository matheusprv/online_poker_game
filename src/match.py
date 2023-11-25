from deck import Deck

import calendar
import time

class Match:

    def getCurrentTimestamp(self) -> int:
        currentGmt = time.gmtime()
        return  calendar.timegm(currentGmt)
        
    def __init__(self) -> None:
        self.players = []
        self.plays = []
        self.initalTime = 0
        self.finalTime = 0
        self.bucket = 0
        self.communityCards = []
        self.deck = Deck()

    def addPlayer(self, newPlayer) -> None:
        self.players.append(newPlayer)

    def addPlay(self, player, action) -> None:
        self.plays.append((player, action))

    def getReport(self) -> str:
        report = "Jogadas:\n"
        for play in self.plays:
            report += f"{play[0]} - {play[1]}\n"
        
        report += f"\n\nTempo de jogo: {(self.finalTime - self.initalTime) // 60}s\n"
        
        report += "\n\n"
        for player in self.players:
            report += f"{player.getName()}:\n\tVitórias: {player.getWins()}\n\tDerrotas: {player.getDefeats()}\n"

        return report

    def flop(self) -> None:
        totalComunnityCards = len(self.communityCards)
        totalNewComunnityCards = 3 if totalComunnityCards == 0 else 1
        newComunityCards = self.deck.distributeCards(totalNewComunnityCards)
        self.communityCards.append(newComunityCards)
    
    def startGame(self) -> None:
        self.initalTime = self.getCurrentTimestamp()
        self.executeGame()
        self.deck.shuffle()

    def executeGame(self):
        pass