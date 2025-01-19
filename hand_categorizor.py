from probability_puzzles import PokerQuiz

from enum import Enum
class HandOutcome(Enum):
    HIGH_CARD = (0, "High Card")
    PAIR = (1, "Pair")
    TWO_PAIR = (2, "Two Pair")
    THREE_OF_A_KIND = (3, "Three of a Kind")
    STRAIGHT = (4, "Straight")
    FLUSH = (5, "Flush")
    FULL_HOUSE = (6, "Full House")
    FOUR_OF_A_KIND = (7, "Four of a Kind")
    STRAIGHT_FLUSH = (8, "Straight Flush")
    ROYAL_FLUSH = (9, "Royal Flush")
    
    def __init__(self, ranking, label):
        self.ranking = ranking
        self.label = label
    
    def __lt__(self, other):
        return self.ranking < other.rankin


def categorize_hand(hole_cards, community_cards):
    pass

if __name__ == "__main__":
    quiz = PokerQuiz()
    hole_cards = quiz.deal_cards(2)
    community_cards = quiz.deal_cards(3)
    print(hole_cards, community_cards)
    print(categorize_hand(hole_cards, community_cards))
