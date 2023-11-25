class Card:
    kinds = ["♣️", "♠️", "♥️", "♦️"]
    values = {
        '2': 2, 
        '3': 3, 
        '4': 4, 
        '5': 5, 
        '6': 6, 
        '7': 7, 
        '8': 8, 
        '9': 9, 
        '10': 10, 
        'Q': 11, 
        'J': 12, 
        'K': 13, 
        'A': 14
    }

    def __init__ (self, value, kind):
        assert type(value) == str
        self.kind = kind
        self.value = value


    def printCard(self):
        print("%2s %s " % (self.value, self.kind))

    def getWeight(self):
        return self.values[self.value]
    
    def getKind(self):
        return self.kind