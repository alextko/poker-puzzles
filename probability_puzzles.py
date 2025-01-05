import random
from collections import defaultdict
from math import factorial

def comb(n, r):
    """Calculate combinations (n choose r)"""
    if n < r:
        return 0
    return factorial(n) // (factorial(r) * factorial(n - r))

class PokerQuiz:
    def __init__(self):
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.suits = ['♠', '♥', '♦', '♣']
        self.deck = [(rank, suit) for rank in self.ranks for suit in self.suits]
        self.rank_values = {rank: idx for idx, rank in enumerate(self.ranks)}
    
    def deal_cards(self, num_cards):
        """Deal specified number of cards"""
        cards = random.sample(self.deck, num_cards)
        for card in cards:
            self.deck.remove(card)
        return cards

    def calculate_probabilities(self, hole_cards, community_cards=None):
        """Calculate probabilities for different poker hands"""
        probabilities = {}
        
        # Reset deck and remove known cards
        self.deck = [(rank, suit) for rank in self.ranks for suit in self.suits]
        for card in hole_cards:
            self.deck.remove(card)
        if community_cards:
            for card in community_cards:
                self.deck.remove(card)

        if community_cards:
            all_cards = hole_cards + community_cards
            current_ranks = [card[0] for card in all_cards]
            current_suits = [card[1] for card in all_cards]
            rank_counts = defaultdict(int)
            suit_counts = defaultdict(int)
            for rank in current_ranks:
                rank_counts[rank] += 1
            for suit in current_suits:
                suit_counts[suit] += 1
            self.calculate_post_flop_probabilities(probabilities, all_cards, rank_counts, suit_counts)
        else:
            self.calculate_pre_flop_probabilities(probabilities, hole_cards)

        return probabilities

    def calculate_pre_flop_probabilities(self, probabilities, hole_cards):
        """Calculate probability of hitting a pair on the flop"""
        rank1, rank2 = hole_cards[0][0], hole_cards[1][0]
        
        if rank1 != rank2:
            num_outs = 6
            cum_prob = 1 
            for i in range(3):
                cum_prob *=  (52-len(hole_cards)- num_outs-i)/(52 - len(hole_cards)-i)
            
            probabilities['Pair'] = round((1-cum_prob) * 100, 2)

        
        return probabilities

    def calculate_post_flop_probabilities(self, probabilities, all_cards, rank_counts, suit_counts):
        """Calculate probabilities of making hands by the river"""
        # For post-flop, we're looking at 2 more cards (turn and river)
        # Starting with 47 cards in deck after hole cards and flop
        
        # Pair calculation (when we have no pair)
        if max(rank_counts.values()) == 1:
            unpaired_ranks = [rank for rank, count in rank_counts.items() if count == 1]
            num_outs = sum(1 for card in self.deck if card[0] in unpaired_ranks)
            cum_prob = 1
            for i in range(2):  # 2 cards coming (turn and river)
                cum_prob *= (47 - num_outs - i)/(47 - i)
            probabilities['Pair'] = round((1 - cum_prob) * 100, 2)
        
        # Three of a kind calculation (when we have a pair)
        elif max(rank_counts.values()) == 2:
            paired_rank = next(rank for rank, count in rank_counts.items() if count == 2)
            num_outs = sum(1 for card in self.deck if card[0] == paired_rank)
            cum_prob = 1
            for i in range(2):
                cum_prob *= (47 - num_outs - i)/(47 - i)
            probabilities['Three of a Kind'] = round((1 - cum_prob) * 100, 2)
        
        # Flush calculation (when we have 4 to a flush)
        max_suit_count = max(suit_counts.values())
        if max_suit_count == 4:
            flush_suit = next(suit for suit, count in suit_counts.items() if count == 4)
            num_outs = sum(1 for card in self.deck if card[1] == flush_suit)
            cum_prob = 1
            for i in range(2):
                cum_prob *= (47 - num_outs - i)/(47 - i)
            probabilities['Flush'] = round((1 - cum_prob) * 100, 2)
        
        # Open-ended straight draw
        straight_outs = self.count_straight_outs_post_flop(all_cards)
        if straight_outs > 0:
            cum_prob = 1
            for i in range(2):
                cum_prob *= (47 - straight_outs - i)/(47 - i)
            probabilities['Straight'] = round((1 - cum_prob) * 100, 2)

    def calculate_draw_probability(self, outs, cards_needed, deck_size):
        """Calculate probability of hitting a draw"""
        if cards_needed == 1:
            return (outs / deck_size) * 100
        elif cards_needed == 2:
            return (outs / deck_size) * ((outs - 1) / (deck_size - 1)) * 100
        return 0

    def count_straight_outs(self, hole_cards):
        """Count number of cards that could complete a straight"""
        rank1, rank2 = self.rank_values[hole_cards[0][0]], self.rank_values[hole_cards[1][0]]
        needed_ranks = set()
        
        # Find all possible straights containing both cards
        for i in range(max(0, min(rank1, rank2) - 4), 
                      min(len(self.ranks) - 4, max(rank1, rank2) + 1)):
            straight_ranks = set(range(i, i + 5))
            if rank1 in straight_ranks and rank2 in straight_ranks:
                needed_ranks.update(straight_ranks - {rank1, rank2})
        
        return sum(1 for card in self.deck if self.rank_values[card[0]] in needed_ranks)

    def count_straight_outs_post_flop(self, cards):
        """Count straight outs after the flop"""
        ranks = sorted([self.rank_values[card[0]] for card in cards])
        needed_ranks = set()
        
        # Check for all possible straight combinations
        for i in range(min(ranks) - 4, max(ranks) + 1):
            possible_straight = set(range(i, i + 5))
            if len(set(ranks) & possible_straight) >= len(cards) - 2:
                needed_ranks.update(possible_straight - set(ranks))
        
        return sum(1 for card in self.deck if self.rank_values[card[0]] in needed_ranks)

    def count_straight_flush_outs(self, hole_cards):
        """Count number of cards that could complete a straight flush"""
        suit = hole_cards[0][1]  # Both cards have same suit for straight flush possibility
        straight_outs = self.count_straight_outs(hole_cards)
        return sum(1 for card in self.deck if card[1] == suit and 
                  self.rank_values[card[0]] in range(min(self.rank_values[hole_cards[0][0]], 
                  self.rank_values[hole_cards[1][0]]) - 4, 
                  max(self.rank_values[hole_cards[0][0]], self.rank_values[hole_cards[1][0]]) + 5))

    def calculate_straight_probability(self, straight_outs):
        """Calculate probability of making a straight"""
        return (straight_outs / 47) * ((straight_outs - 1) / 46) * ((straight_outs - 2) / 45) * 100

    def calculate_straight_flush_probability(self, straight_flush_outs):
        """Calculate probability of making a straight flush"""
        return (straight_flush_outs / 47) * ((straight_flush_outs - 1) / 46) * ((straight_flush_outs - 2) / 45) * 100

    def calculate_royal_flush_probability(self, hole_cards):
        """Calculate probability of making a royal flush"""
        suit = hole_cards[0][1]
        needed_ranks = {'10', 'J', 'Q', 'K', 'A'} - {hole_cards[0][0], hole_cards[1][0]}
        royal_outs = sum(1 for card in self.deck if card[1] == suit and card[0] in needed_ranks)
        return (royal_outs / 47) * ((royal_outs - 1) / 46) * ((royal_outs - 2) / 45) * 100

    def calculate_full_house_probability(self, hole_cards):
        """Calculate probability of making a full house"""
        if hole_cards[0][0] == hole_cards[1][0]:
            # Already have a pair
            remaining_ranks = set(card[0] for card in self.deck)
            trip_prob = len([c for c in self.deck if c[0] == hole_cards[0][0]]) / 47
            pair_prob = sum(len([c for c in self.deck if c[0] == r]) / 47 for r in remaining_ranks)
            return trip_prob * pair_prob * 100
        else:
            # Need to make two pair and then boat
            return (6 / 47) * (5 / 46) * (4 / 45) * 100

    def quiz(self):
        """Run the poker probability quiz"""
        while True:
            stage = input("\nWould you like to quiz pre-flop or post-flop? (pre/post): ").lower()
            if stage in ['pre', 'post']:
                break
            print("Please enter 'pre' or 'post'")

        hole_cards = self.deal_cards(2)
        community_cards = self.deal_cards(3) if stage == 'post' else None
        
        print(f"\nYour hole cards are: {hole_cards[0][0]}{hole_cards[0][1]} {hole_cards[1][0]}{hole_cards[1][1]}")
        if community_cards:
            print(f"Flop cards are: {' '.join(f'{card[0]}{card[1]}' for card in community_cards)}")
        
        actual_probabilities = self.calculate_probabilities(hole_cards, community_cards)
        
        for hand, actual_prob in actual_probabilities.items():
            if actual_prob > 0:  # Only quiz on possible hands
                while True:
                    try:
                        guess = float(input(f"\nWhat is the probability (in %) of making a {hand} by the river? "))
                        difference = abs(guess - actual_prob)
                        
                        print(f"The actual probability is {actual_prob}%")
                        if difference <= 5:
                            print("Great guess! Within 5% of the actual probability.")
                        elif difference <= 10:
                            print("Not bad! Within 10% of the actual probability.")
                        else:
                            print("Keep practicing! That was off by more than 10%.")
                        break
                    except ValueError:
                        print("Please enter a valid number.")

def main():
    quiz = PokerQuiz()
    while True:
        quiz.quiz()
        if input("\nWould you like another question? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main() 