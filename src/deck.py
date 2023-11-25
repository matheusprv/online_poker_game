import random
from card import Card

class Deck:
    def __init__(self) -> None:
        self.cards = []
        self.clear_deck()

    # Shuffle the current decks's list of cards
    def shuffle(self) -> None:
        random.shuffle(self.cards)

    # Given a number of cards, it will remove from the deck N cards and return it 
    def distributeCards(self, number_of_cards = 1) -> list:
        return [self.cards.pop(0) for _ in range(number_of_cards)]
    
    # Given an array of cards, it will put them back on the deck
    def returnCard(self, cards_to_return) -> None:
        for card in cards_to_return:
            self.cards.append(card)

    def printDeck(self) -> None:
        print("Number of cards on deck: " + str(len(self.cards)))
        for card in self.cards:
            card.print_card()

    
    # Begins or restart a deck restarting the cards. The cards aren't shuffle 
    def clearDeck(self) -> None:
        self.cards.clear()
        self.cards = [Card(value, kind) for value in Card.values for kind in Card.kinds]


if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()

    myCards = [deck.distributeCards() for _ in range(2)]

