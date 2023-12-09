from deck import Deck

import calendar
import time
from copy import copy

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

    def getPlayers(self):
        return self.players

    def addPlayer(self, newPlayer) -> None:
        self.players.append(newPlayer)

    def removePlayer(self, player) -> None:
        self.players.remove(player)

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

    def addToBucket(self, value) -> None:
        self.bucket += value

    # Return the total of active players. If it is one, return the player, otherwise return None
    def totalActivePlayers(self):
        total = 0
        activePlayers = []
        for player in self.getPlayers():
            if player.isActive(): 
                total += 1
                activePlayers.append(player)

        return total, activePlayers[0] if total == 1 else None

    def printCommunityCards(self) -> None:
        for card in self.communityCards:
            card.printCard()

    def printFinalCards(self, player) -> None:
        count = 1
        for card in player.getCards() + self.communityCards:
            print(f"{count}- ", end='')
            card.printCard()
            count += 1

    def resetTable(self) -> None:
        # Reset bucket
        self.bucket = 0
        
        # Reset community cards
        self.deck.returnCard(self.communityCards)
        self.communityCards = []

        # Reset the deck by shuffling it
        self.deck.shuffle()

        #Retrive the player's cards to the deck
        for player in self.getPlayers():
            player.resetSelectedCards()
            if player.isActive():
                self.deck.returnCard(player.retriveCards())
            else:
                player.setActive(True)                
                
            if player.getChips() == 0:
                self.removePlayer(player)

    def flop_turn_river(self) -> None:
        totalComunnityCards = len(self.communityCards)
        totalNewComunnityCards = 3 if totalComunnityCards == 0 else 1
        
        for newComunityCards in self.deck.distributeCards(totalNewComunnityCards):
            self.communityCards.append(newComunityCards)

    def betRound(self, countBetRound, position, positionBB, positionSB, bet, betBB, betSB) -> None:
        players = self.getPlayers()
        totalPlayers = len(players)

        for _ in range(0, totalPlayers):
            player = players[position]
            if(player.isActive()):

                # The player will make a decision to what he is going to do
                # If the action is to raise, but the player doesn't have enough chips, it will go to pay and will do an All-In
                action = '_'
                validActions = ['f', 'p', 'r']
                actionsText = f"{player.getName()} - Ações: \nF - Fold \nP - Pagar \nR - Aumentar"

                minimunBet = bet 

                if countBetRound == 1:
                    if position == positionBB: minimunBet = bet - betBB 
                    elif position == positionSB: minimunBet = bet - betSB 

                # If the user is BigBlind, he can check if the bet didn't raise                
                if (position == positionBB and bet == betBB) or (countBetRound > 1 and bet == 0):
                    validActions.append('c')
                    actionsText += "\nC - Check"

                # Loop until the user enters a valid action
                while(action not in validActions):
                    action = input(actionsText+"\nOpção: ").lower()
                    if(action == 'r' and player.getChips() <= bet): action = 'p'

                if action == "f":
                    # The player retrive the cards to the deck and become inactive
                    self.deck.returnCard(player.retriveCards())
                    player.setActive(False)
                    self.addPlay(player, "Fold")

                elif action == "p":
                    #Pay the bet or go All-In
                    if player.getChips() - minimunBet >= 0:
                        player.setChips(player.getChips() - minimunBet)
                        self.addToBucket(minimunBet)
                    else:
                        self.addToBucket(player.getChips())
                        minimunBet = player.getChips()
                        player.setChips(0)
                    self.addPlay(player, f"Pagar:{minimunBet}")
                    
                elif action == "r":
                    #Put the higher value than the current bet
                    while 1:
                        bet_temp = int(input(f"{player.getName()} - Qual será o valor da aposta (Valor mínimo para aposta {minimunBet+1}): "))
                        
                        if player.getChips() - bet_temp >= 0 and bet_temp >= minimunBet:
                            player.setChips(player.getChips() - bet_temp)
                            break
                        else:
                            print("Valor inválido da aposta")
                            
                    bet += bet_temp
                    self.addToBucket(bet_temp)
                    self.addPlay(player, f"Raise(Aumentar):{bet_temp}")
                
                print(f"Bucket: {self.bucket}")
    
            position = (position + 1) % totalPlayers    

    def startGame(self) -> None:
        self.initalTime = self.getCurrentTimestamp()
        self.deck.shuffle()
        
        roundCounter = 1
        while len(self.getPlayers()) > 1:
            self.executeGame(roundCounter)
            roundCounter += 1

    def executeGame(self, roundCounter) -> None:
        players = self.getPlayers()
        totalPlayers = len(players)

        #Defining who is going to be big blind and who is going to be the samll blind
        positionSB = roundCounter % totalPlayers
        positionBB = (positionSB + 1) % totalPlayers

        #Big Blind define the bet
        bet = 0
        player = None
        while 1:
            player = players[positionBB]
            bet = int(input(f"{player.getName()} - Qual será o valor da aposta inicial: "))
            
            if player.getChips() - bet >= 0:
                player.setChips(player.getChips() - bet)
                break
            else:
                print("Valor inválido da aposta")

        betBB = bet
        self.addToBucket(bet)
        self.addPlay(player=player, action=f"Aposta:{bet}")

        # Making small blind bet
        betSB = betBB // 2
        player = players[positionSB]

        if player.getChips() - betSB > 0:
            player.setChips(player.getChips() - betSB)
            self.addToBucket(betSB)
        else:
            self.addToBucket(player.getChips())
            betSB = player.getChips()
            player.setChips(0)
        
        self.addPlay(player=player, action=f"Aposta:{betSB}")

        #Distribute cards
        position = positionSB
        for _ in range(0, totalPlayers):
            player = players[position % totalPlayers]
            player.setCards(self.deck.distributeCards(2))
            position += 1

            print(f"{player.getName()}")
            for card in player.getCards():
                card.printCard()

        #First bet round
        position = (positionBB + 1)  % totalPlayers
        self.betRound(1, position, positionBB, positionSB, bet, betBB, betSB)

        # Check if there is only one active player, if so, then it will receive the chips of the bucket
        totalActive, player = self.totalActivePlayers()
        if totalActive == 1:
            player.setChips(player.getChips() + self.bucket)
            print(f"Ganhador: {player.getName()}")
            self.resetTable()
            return

        #Second bet round
        position = positionSB
        #flop - shows three community cards on the table
        self.flop_turn_river()
        print("Cartas Comunitárias")
        self.printCommunityCards()
        self.betRound(2, position, positionBB, positionSB, 0, betBB, betSB)

        # Check if there is only one active player, if so, then it will receive the chips of the bucket
        totalActive, player = self.totalActivePlayers()
        if totalActive == 1:
            player.setChips(player.getChips() + self.bucket)
            print(f"Ganhador: {player.getName()}")
            self.resetTable()
            return
            
        #Third bet round
        #turn - show the 4th community card
        self.flop_turn_river()
        print("Cartas Comunitárias")
        self.printCommunityCards()
        self.betRound(3, position, positionBB, positionSB, 0, betBB, betSB)
        
        # Check if there is only one active player, if so, then it will receive the chips of the bucket
        totalActive, player = self.totalActivePlayers()
        if totalActive == 1:
            player.setChips(player.getChips() + self.bucket)
            print(f"Ganhador: {player.getName()}")
            self.resetTable()
            return
        
        #Fourth bet round
        #river - show the 5th community card
        self.flop_turn_river()
        print("Cartas Comunitárias")
        self.printCommunityCards()
        self.betRound(4, position, positionBB, positionSB, 0, betBB, betSB)

        # Check if there is only one active player, if so, then it will receive the chips of the bucket
        totalActive, player = self.totalActivePlayers()
        if totalActive == 1:
            player.setChips(player.getChips() + self.bucket)
            self.resetTable()
            print(f"Ganhador: {player.getName()}")
            return

        #choosing the 5 card hand
        for player in players:
            self.printFinalCards(player)
            selectedCards = []

            #Making the user select five different cards
            for _ in range(5):
                select = int(input(f"{player.getName()} - Digite o índice da carta que deseja selecionar: "))
                while select in selectedCards:
                    print("Valor já selecionado.")
                    select = int(input(f"{player.getName()} - Digite o índice da carta que deseja selecionar: "))
                
                selectedCards.append(select)

            #Copying the cards to the selectedCards player attribute
            for selected in selectedCards:
                if(selected == 1 or selected == 2):
                    selected -= 1
                    card = copy(player.getCards()[selected])
                    player.addSelectedCard(card)
                else:
                    selected -= 3 #-1 from user input and -2 due to the player's cards 
                    card = copy(self.communityCards[selected])
                    player.addSelectedCard(card)

        # Check what is the player with the highest pontuation
        winner = players[0]
        winnerCardPoints = winner.countCardsPoints()

        for player in players[1:]:
            playerCardPoints = player.countCardsPoints()
            if player.isActive and playerCardPoints > winnerCardPoints:
                winner = player
                winnerCardPoints = playerCardPoints

        # Give the bucket's chips to the winner
        winner.setChips(winner.getChips() + self.bucket)

        print(f"Ganhador: {winner.getName()}")

        self.resetTable()