from deck import Deck

import calendar
import time
from time import sleep
from copy import copy
from itertools import cycle, islice


from constants import *

FIRST_BETTING_ROUND = 2
LAST_BETTING_ROUND  = 4

GREEN = "green"
RED   = "red"
BLUE  = "blue"

class Match:

    def getCurrentTimestamp(self) -> int:
        currentGmt = time.gmtime()
        return  calendar.timegm(currentGmt)
        
    def __init__(self, matchId, sendMessage, recvMessage, quitPlayer) -> None:
        self.matchId = matchId
        self.newMatch()

        self.sendMessage = sendMessage
        self.recvMessage = recvMessage
        self.quitPlayer = quitPlayer

    def newMatch(self):
        self.players = []
        self.plays = []
        self.initalTime = 0
        self.finalTime = 0
        self.bucket = 0
        self.communityCards = []
        self.deck = Deck()
        self.inProgress = False

    def coloredText(self, text, color) -> str:
        if color == GREEN: return "\033[92m" + text + "\033[0m"
        if color == RED:   return "\033[91m" + text + "\033[0m"

    def getPlayers(self):
        return self.players

    def addPlayer(self, newPlayer) -> None:
        self.players.append(newPlayer)

    """
        Remove a player from the array of players. Used when the player ran out of chips
    """
    def removePlayer(self, player) -> None:
        if len(player.cards) > 0:
            self.deck.returnCard(player.retriveCards())
        self.sendMessage(player=player, privateMsg="SESSION REMOVED")
        self.players.remove(player)

    def addPlay(self, player, action) -> None:
        self.plays.append((player.getName(), action))

    def setInProgress(self, inProgress) -> None:
        self.inProgress = inProgress

    def isInProgress(self) -> bool:
        return self.inProgress

    def formatElapsedTime(self):
        elapsed_seconds = self.finalTime - self.initalTime
        minutes, seconds = divmod(elapsed_seconds, 60)
        elapsed_time_formatted = f"{minutes:02}:{seconds:02}"
        return elapsed_time_formatted

    """
        Generate a report with all the plays from the game and wins/defeats from each player
    """
    def getReport(self) -> str:
        report = "="*50
        report += "\nJogadas:\n"
        for play in self.plays:
            report += f"{play[0]} - {play[1]}\n"
        
        report += f"\n\nTempo de jogo: {self.formatElapsedTime()}\n"
        
        report += "\n\n"
        for player in self.players:
            report += f"{player.getName()}:\n\tVitórias: {player.getWins()}\n\tDerrotas: {player.getDefeats()}\n\tFichas: {player.getChips()}\n"

        report += "="*50

        return report

    def addToBucket(self, value) -> None:
        self.bucket += value

    def chipsInformations(self, player, bucket, bet) -> str:
        output = "="*50
        output += f"\nFichas que você possui: {player.getChips()}"
        output += f"\nBucket: {bucket}"
        output += f"\nAposta Atual: {bet}\n"
        output += "="*50 + "\n"
        return output

    
    """
        Return the total of active players. 
        If it is one, return the player, otherwise return None
    """
    def totalActivePlayers(self):
        total = 0
        activePlayers = []
        for player in self.getPlayers():
            if player.isActive(): 
                total += 1
                activePlayers.append(player)

        return total, activePlayers[0] if total == 1 else None
    
    """
        Return the total of players that are still onlin in the game
    """
    def totalOnlinePlayers(self) -> int:
        total = 0
        for player in self.getPlayers():
            if player.isOnline(): 
                total += 1

        return total

    """
        Generate a string containing the community cards
    """
    def strCommunityCards(self) -> str:
        strCards = ""
        for card in self.communityCards:
            strCards += "\n" + card.stringCard()
        return strCards

    """
        Guarantee that an input coming from the user will be a numeric value. If it is not, then an error message will be sent
    """
    def receiveNumericMessage(self, player, errorText) -> int:
        receivedValue = self.recvMessage(player.getSocket())
        while not receivedValue.isnumeric():
            self.sendMessage(player, privateMsg = errorText, waitingAnswer=True)
            receivedValue = self.recvMessage(player.getSocket())
            if receivedValue == '-1':
                break

        if receivedValue == '-1': receivedValue = '0'

        return int(receivedValue)

    """
        Format all the community and the player's cards into a single string with the index to choose them
    """
    def strFinalCards(self, player) -> str:
        count = 1

        strCards = "\nCartas do Jogador:\n"
        for card in player.getCards():
            strCards += f"\t{count}: {card.stringCard()}\n" 
            count += 1

        strCards += "Cartas da Mesa:\n"
        for card in self.communityCards:
            strCards += f"\t{count}: {card.stringCard()}\n" 
            count += 1

        return strCards

    """
        Restart the table putting the bucket in 0 and returning all the player's cards
        Players that are inactive will now become active
    """
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
            elif player.isOnline():
                player.setActive(True)                
            
            print(f"{player.getName()} - chips: {player.getChips()}")
            if player.getChips() == 0.0 or player.getChips() == 0:
                self.removePlayer(player)

    def returnPlayerCardsToDeck(self, player) -> None:
        self.deck.returnCard(player.retriveCards())

    def flop_turn_river(self) -> None:
        totalComunnityCards = len(self.communityCards)
        totalNewComunnityCards = 3 if totalComunnityCards == 0 else 1
        
        for newComunityCards in self.deck.distributeCards(totalNewComunnityCards):
            self.communityCards.append(newComunityCards)


    """
        Check if all the players on the match are "Pronto" 
    """
    def checkReadyPlayers(self) -> bool:
        #print(f"Checando {len(self.getPlayers())} jogadores da partida {self.matchId}")
        
        if(len(self.getPlayers())) <= 1:
            return False

        for player in self.getPlayers():
            if player.getReady() == False:
                return False
            
        return True


    """
        Make Big blind and small blind bets
        Return values:{
            bet : Value of the current bet
            betBB : Big Blind bet
            betSB : Small Blind bet
        }
    """
    def blindBet(self, playerSB, playerBB):
       
        bet = 0        
        while 1:
            self.sendMessage(playerBB, f"Big Blind {playerBB.getName()} definindo a aposta", self.chipsInformations(playerBB, self.bucket, bet) + f"{playerBB.getName()} - Qual será o valor da aposta inicial: ", waitingAnswer=True)
            text = self.coloredText("O valor deve ser um inteiro positivo", RED) + f"\n{playerBB.getName()} - Qual será o valor da aposta inicial: "
            bet = self.receiveNumericMessage(playerBB, errorText= text)
            
            if playerBB.getChips() - bet >= 0 and bet > 1:
                playerBB.setChips(playerBB.getChips() - bet)
                break
            elif not playerBB.isOnline():
                self.addPlay(player=playerBB, action=f"{playerBB.getName()} saiu da partida")
                self.sendMessage(publicMsg = f"{playerBB.getName()} saiu da partida")
                bet = 0
                break
            else:
                self.sendMessage(playerBB, privateMsg=self.coloredText("Valor inválido da aposta", RED))

        betBB = bet
        self.addToBucket(bet)
        self.addPlay(player=playerBB, action=f"Aposta:{bet}")
        self.sendMessage(publicMsg = f"Jogador {playerBB.getName()} apostou {bet} fichas sendo o Big Blind.")

        # Making small blind bet
        betSB = betBB // 2

        if playerSB.getChips() - betSB > 0:
            playerSB.setChips(playerSB.getChips() - betSB)
            self.addToBucket(betSB)
        else:
            self.addToBucket(playerSB.getChips())
            betSB = playerSB.getChips()
            playerSB.setChips(0)
        
        self.addPlay(player=playerSB, action=f"Aposta:{betSB}")
        self.sendMessage(publicMsg = f"Jogador {playerSB.getName()} apostou {betSB} fichas sendo o Small Blind.")

        return bet, betBB, betSB

    """
        Make all player's bet
    """
    def betRound(self, countBetRound, position, playerBB, playerSB, bet, betBB, betSB) -> None:
        
        index = self.getPlayers().index(position)
        players = self.getPlayers()[index:] + self.getPlayers()[:index]
        for player in players:
            print(f"\tjogador {player.getName()} - Ativo: {player.isActive()}")

        for player in players:            
            numberOfActivePlayers, _ = self.totalActivePlayers() 
            if (numberOfActivePlayers == 1): break
            if(not player.isActive()): continue

            print(f"{player.getName()} fazendo a aposta")

            # The player will make a decision to what he is going to do
            # If the action is to raise, but the player doesn't have enough chips, it will go to pay and will do an All-In
            action = '_'
            validActions = ['f', 'p', 'r', 'q', '-1']
            actionsText = f"{player.getName()} - Ações: \nF - Fold \nP - Pagar \nR - Aumentar"

            minimunBet = bet 

            if countBetRound == 1:
                if player.getId() == playerBB.getId(): minimunBet = bet - betBB 
                elif player.getId() == playerSB.getId(): minimunBet = bet - betSB 

            # If the user is BigBlind, he can check if the bet didn't raise                
            if (player.getId() == playerBB.getId() and bet == betBB) or (countBetRound > 1 and bet == 0):
                validActions.append('c')
                actionsText += "\nC - Check"

            actionsText += "\nQ - Sair do jogo."

            # Loop until the user enters a valid action
            while(action not in validActions):
                self.sendMessage(player, privateMsg= self.chipsInformations(player, self.bucket, bet) + actionsText + "\nOpção: ", waitingAnswer=True)
                action = self.recvMessage(player.getSocket()).lower()
                
                if(action == 'r' and player.getChips() <= bet): action = 'p'

            print(f"{player.getName()} - {action}")

            if action == "f":
                # The player retrive the cards to the deck and become inactive
                self.deck.returnCard(player.retriveCards())
                player.setActive(False)
                self.addPlay(player, "Fold")
                self.sendMessage(publicMsg = f"Jogador {player.getName()} realizou uma ação de Fold")

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
                self.sendMessage(publicMsg = f"Jogador {player.getName()} pagou {minimunBet} ficha(s)")
                
            elif action == "r":
                #Put the higher value than the current bet
                
                textMinimunBet = f"{player.getName()} - Qual será o valor da aposta (Valor mínimo para aposta {minimunBet+1}): "
                
                while 1:
                    self.sendMessage(
                        player, 
                        f"Jogador {player.getName()} aumentando a aposta",
                        self.chipsInformations(player, self.bucket, bet) + textMinimunBet, 
                        waitingAnswer=True)
                    
                    text = self.coloredText("O valor deve ser um inteiro positivo", RED) + textMinimunBet
                    bet_temp = self.receiveNumericMessage(player, errorText = text)
                    
                    if player.getChips() - bet_temp >= 0 and bet_temp > minimunBet:
                        player.setChips(player.getChips() - bet_temp)
                        break
                    elif not player.isOnline():
                        self.addPlay(player=player, action=f"{player.getName()} saiu da partida")
                        self.sendMessage(publicMsg = f"{player.getName()} saiu da partida")
                        bet_temp = 0
                        break
                    else:
                        self.sendMessage(player, privateMsg=self.coloredText("Valor inválido da aposta", RED))
                        
                bet += bet_temp
                self.addToBucket(bet_temp)
                self.addPlay(player, f"Raise(Aumentar):{bet_temp}")
                
                self.sendMessage(publicMsg = f"Jogador {player.getName()} aumentou a aposta para {bet_temp} fichas")
                self.sendMessage(publicMsg = f"Bucket: {self.bucket}")
            
            elif action == "q" or action == '-1':
                self.addPlay(player, f"Saiu do jogo")
                self.sendMessage(publicMsg = f"Jogador {player.getName()} saiu do jogo", player = player, privateMsg="SESSION FINISHED")
                
                self.deck.returnCard(player.retriveCards())
                player.setOffline()

    """
        Check if there is only one active player or online, if so, then it will receive the chips of the bucket
        Return True if the match is finished. False otherwise
    """
    def checkTotalActivePlayers(self):
        totalActive, player = self.totalActivePlayers()
        if totalActive == 1:
            player.setChips(player.getChips() + self.bucket)
            player.wins += 1
            self.sendMessage(publicMsg = f"Ganhador: {player.getName()}")

            for p in self.getPlayers():
                if p != player:
                    p.defeats += 1

            #self.resetTable()
            return True
        
        return False

    """
        Distribute the initial cards among the players
    """
    def distributeCards(self, playerSB):
        index = self.getPlayers().index(playerSB)
        players = self.getPlayers()[index:] + self.getPlayers()[:index]

        for player in players:
            player.setCards(self.deck.distributeCards(2))

            cardMessage = f"Cartas de {player.getName()}"
            for card in player.getCards():
                cardMessage += "\n" + card.stringCard()
            
            cardMessage += '\n'
            
            #verificacao adicionada para realizar teste da função sem a necessidade de enviar dados para um socket de jogador
            if self.sendMessage != None:
                self.sendMessage(player, privateMsg=cardMessage)

    """
        The player will choose the five cards that will compose his hand
    """
    def chooseFiveCards(self):
        for player in self.getPlayers():
            if not player.isActive():
                continue

            cardsToChoose = self.strFinalCards(player)

            self.sendMessage(player, publicMsg= cardsToChoose)
            selectedCards = []

            #Making the user select five different cards

            selectionCardMessage = f"{player.getName()} - Digite o índice da carta que deseja selecionar: "

            for i in range(5):
                self.sendMessage(
                    player, 
                    f"Jogador {player.getName()} selecionando a {i+1}ª carta.", selectionCardMessage,
                    waitingAnswer=True
                )
                select = self.receiveNumericMessage(player, self.coloredText("O valor deve ser um inteiro positivo", RED) + "\n" + selectionCardMessage)

                while select < 1 or select > 7: 
                    self.sendMessage(player, 
                                     privateMsg=self.coloredText("Valor inválido!", RED) + "\nDigite o índice da carta que deseja selecionar: ", 
                                     waitingAnswer=True
                                     )
                    select = self.receiveNumericMessage(player, self.coloredText("O valor deve ser um inteiro positivo", RED) + "\n" + selectionCardMessage)
                
                while select in selectedCards:
                    self.sendMessage(player, 
                                     privateMsg="Valor já selecionado \nDigite o índice da carta que deseja selecionar: ", 
                                     waitingAnswer=True
                                     )
                    select = self.receiveNumericMessage(player, self.coloredText("O valor deve ser um inteiro positivo", RED) + "\n" + selectionCardMessage)
                
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

    """
        Check what player had the better cards and is the winner
    """
    def checkWinner(self):
        players = self.getPlayers()
        winner = None
        winnerCardPoints = -1

        for player in players:
            player.defeats += 1
            if not player.isActive(): continue
            playerCardPoints = player.countCardsPoints()
            if playerCardPoints > winnerCardPoints:
                winner = player
                winnerCardPoints = playerCardPoints

        # Give the bucket's chips to the winner
        winner.setChips(winner.getChips() + self.bucket)

        winner.wins += 1
        winner.defeats -= 1

        self.sendMessage(publicMsg= f"Ganhador: {player.getName()}")

    def removeOfflinePlayers(self):
        for player in self.getPlayers():
            if not player.isOnline():
                self.quitPlayer(player)

    def startGame(self) -> None:
        self.deck.shuffle()
        
        roundCounter = 1
        while self.totalOnlinePlayers() > 1:
            self.resetTable()
            
            if self.totalOnlinePlayers() <= 1: break
            #Starting and finishing a match
            self.initalTime = self.getCurrentTimestamp()
            self.executeGame(roundCounter)
            self.finalTime = self.getCurrentTimestamp()

            # Sending the report to all players
            self.sendMessage(publicMsg = self.getReport())

            sleep(1)
            self.resetTable()
            self.removeOfflinePlayers()
            self.setInProgress(False)
            roundCounter += 1
    """
        Execute a gaming round
    """
    def executeGame(self, roundCounter) -> None:
        
        self.setInProgress(True)
        players = self.getPlayers()

        #Defining who is going to be big blind and who is going to be the samll blind
        positionSB = roundCounter % len(players)
        positionBB = (positionSB + 1) % len(players)
        playerSB = players[positionSB]
        playerBB = players[positionBB]

        if self.checkTotalActivePlayers(): return 
        #make big blind and small blind bets'
        bet, betBB, betSB = self.blindBet(playerSB, playerBB)
        print("Blind bets feita")

        if self.checkTotalActivePlayers(): return 
        #Distribute cards
        print("Distribuindo cartas")
        self.distributeCards(playerSB)
        print("Cartas distribuidas")
        sleep(0.2)

        if self.checkTotalActivePlayers(): return 
        #First bet round
        nextPosition = players.index(playerBB) + 1
        nextPosition = nextPosition if nextPosition < len(players) else 0
        position = players[nextPosition]
        self.betRound(1, position, playerBB, playerSB, bet, betBB, betSB)

        # Check if there is only one active player, if so, then it will receive the chips of the bucket
        if self.checkTotalActivePlayers(): return 

        playerPosition = playerSB

        """
            Making all betting rounds
        """
        for i in range(FIRST_BETTING_ROUND, LAST_BETTING_ROUND + 1):
            self.flop_turn_river()
            
            communityCardsMessage = "Cartas Comunitárias" + self.strCommunityCards()
            self.sendMessage(publicMsg = communityCardsMessage)

            if self.checkTotalActivePlayers(): return 
            self.betRound(i, playerPosition, playerBB, playerSB, 0, betBB, betSB)

            # Check if there is only one active player, if so, then it will receive the chips of the bucket
            if self.checkTotalActivePlayers(): return 


        """
            Bets finished
        """
        #choosing the 5 card hand
        self.chooseFiveCards()

        # Check what is the player with the highest pontuation
        self.checkWinner()

