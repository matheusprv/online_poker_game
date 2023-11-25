class Card:
    kinds = ["♣️", "♠️", "♥️", "♦️"]
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Q', 'J', 'K', 'A']

    def __init__ (self, value, kind):
        self.kind = kind
        self.value = value

    def print_card(self):
        print("%2s %s " % (self.value, self.kind))