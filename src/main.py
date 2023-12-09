from match import Match
from player import Player

p1 = Player("Pedro")
p2 = Player("Matheus")

partida = Match()
partida.addPlayer(p1)
partida.addPlayer(p2)

partida.startGame()