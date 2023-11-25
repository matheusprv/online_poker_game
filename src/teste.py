from deck import Deck
from player import Player
from card import Card

countSameValues = {
    '2': 1,
    '5': 3,
    '7': 1
}

# print(max(countSameValues.values()))

# print('\n')

# print(2 in countSameValues.values())
# print(3 in countSameValues.values())

# print('\n')

# print(list(countSameValues.values()).count(1))
# print(list(countSameValues.values()).count(3))

if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()

    player = Player("player")

    kinds = ["♣️", "♠️", "♥️", "♦️"]

    player.setCards([
        Card("K","♣️"),
        Card("J","♥️"),
        Card("10","♥️"),
        Card("2","♦️"),
        Card("5","♠️")
    ])
    print(player.countCardsPoints())

    player.setCards([
        Card("2","♥️"),
        Card("6","♥️"),
        Card("8","♠️"),
        Card("A","♥️"),
        Card("A","♥️")
    ])
    print(player.countCardsPoints())

    player.setCards([
        Card("8","♥️"),
        Card("8","♠️"),
        Card("6","♥️"),
        Card("6","♣️"),
        Card("3","♥️")
    ])
    print(player.countCardsPoints())

    player.setCards([
        Card("K","♥️"),
        Card("K","♥️"),
        Card("K","♣️"),
        Card("4","♣️"),
        Card("7","♥️")
    ])
    print(player.countCardsPoints())


    player.setCards([
        Card("2","♥️"),
        Card("3","♦️"),
        Card("4","♣️"),
        Card("5","♠️"),
        Card("6","♥️")
    ])

    print(player.countCardsPoints())

    player.setCards([
        Card('Q', "♣"),
        Card('9', "♣"),
        Card('10', "♣"),
        Card('7', "♣"),
        Card('4', "♣"),]
    )
    print(player.countCardsPoints())

    player.setCards(
        [Card('10', "♠"),
        Card('10', "♥"),
        Card('K', "♣"),
        Card('K', "♥"),
        Card('K', "♠"),]
    )
    print(player.countCardsPoints())

    player.setCards([
        Card('7', "♦"),
        Card('A', "♦"),
        Card('A', "♠"),
        Card('A', "♥"),
        Card('A', "♣")]
    )
    print(player.countCardsPoints())

    player.setCards([
        Card('5', "♠"),
        Card('6', "♠"),
        Card('7', "♠"),
        Card('8', "♠"),
        Card('9', "♠"),]
    )
    print(player.countCardsPoints())

    player.setCards(
        [Card('10', "♥"),
        Card('J', "♥"),
        Card('Q', "♥"),
        Card('K', "♥"),
        Card('A',"♥")]
    )
    print(player.countCardsPoints())
