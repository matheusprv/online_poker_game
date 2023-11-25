import random
from card import Card

class Deck:
    def __init__(self) -> None:
        self.cards = []
        self.createDeck()

    # Shuffle the current decks's list of cards
    def shuffle(self) -> None:
        random.shuffle(self.cards)

    # Given a number of cards, it will remove from the deck N cards and return it 
    def distributeCards(self, numberOfCards = 1) -> list:
        return [self.cards.pop(0) for _ in range(numberOfCards)]
    
    # Given an array of cards, it will put them back on the deck
    def returnCard(self, cardsToReturn) -> None:
        for card in cardsToReturn:
            self.cards.append(card)

    def printDeck(self) -> None:
        print("Number of cards on deck: " + str(len(self.cards)))
        for card in self.cards:
            card.printCard()

    
    # Begins or restart a deck restarting the cards. The cards aren't shuffle 
    def createDeck(self) -> None:
        self.cards.clear()
        self.cards = [Card(value, kind) for value in Card.values.keys() for kind in Card.kinds]


if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()

    myCards = deck.distributeCards(5)

    for c in myCards:
        c.printCard()

    myCards.sort(key = lambda card : card.getWeight())
    print("="*15)
    for c in myCards:
        c.printCard()
    