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

    def getPlayers(self):
        return self.players

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


    def flop_turn_river(self) -> None:
        totalComunnityCards = len(self.communityCards)
        totalNewComunnityCards = 3 if totalComunnityCards == 0 else 1
        newComunityCards = self.deck.distributeCards(totalNewComunnityCards)
        self.communityCards.append(newComunityCards)
    
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
            bet = int(input("Qual será o valor da aposta inicial: "))
            player = players[positionBB]
            
            if player.getChips() - bet > 0:
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

        #First bet round
        position = (positionBB + 1)  % totalPlayers
        for _ in range(0, totalPlayers):
            player = players[position]
            if(player.isActive()):

                # The player will make a decision to what he is going to do
                # If the action is to raise, but the player doesn't have enough chips, it will go to pay and will do an All-In
                action = '_'
                validActions = ['f', 'p', 'r']
                actionsText = "Ações: \nF - Fold \nP - Pagar \nR - Aumentar"

                #!Verificar para as proximas rodadas de aposta
                minimunBet = bet 
                if position == positionBB: minimunBet = bet - betBB 
                elif position == positionSB: minimunBet = bet - betSB 

                # If the user is BigBlind, he can check if the bet didn't raise                
                if position == positionBB and bet == betBB:
                    validActions.append('c')
                    actionsText += "\nC - Check"

                # Loop until the user enters a valid action
                while(action not in validActions):
                    action = input(actionsText).lower()
                    if(action == 'r' and player.getChips() <= bet): action = 'p'

                if action == "f":
                    # The player retrive the cards to the deck and become inactive
                    self.deck.returnCard(player[position].retriveCards())
                    player[position].setActive(False)
                    self.addPlay(player, "Fold")

                elif action == "p":
                    #Pay the bet or go All-In
                    if player.getChips() - minimunBet > 0:
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
                        bet_temp = int(input(f"Qual será o valor da aposta (Valor mínimo para aposta{minimunBet+1}): "))
                        
                        if player.getChips() - bet_temp > 0 and bet_temp > minimunBet:
                            player.setChips(player.getChips() - bet_temp)
                            break
                        else:
                            print("Valor inválido da aposta")
                            
                    bet = bet_temp
                    self.addToBucket(bet)
                    self.addPlay(player, f"Raise(Aumentar):{bet}")

        # Check if there is only one active player, if so, then it will receive the chips
        totalActive, player = self.totalActivePlayers()
        if totalActive == 1:
            player.setChips(player.getChips() + self.bucket)
            self.bucket = 0
            return

        #Second bet round
        bet = 0
        position = positionSB