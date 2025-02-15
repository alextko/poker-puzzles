import random
from collections import defaultdict
from math import factorial
from validator import probabilityValidator

def comb(n, r):
    """Calculate combinations (n choose r)"""
    if n < r:
        return 0
    return factorial(n) // (factorial(r) * factorial(n - r))

class PokerQuiz:
    def __init__(self):
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.suits = ['♠', '♥', '♦', '♣']
        self.deck = [[rank, suit] for rank in self.ranks for suit in self.suits]
        self.rank_values = {rank: idx for idx, rank in enumerate(self.ranks)}
        self.correct_answers = 0
        self.total_questions = 0
    
    def deal_cards(self, num_cards):
        """Deal specified number of cards from the deck and remove them."""
        cards = random.sample(self.deck, num_cards)
        for card in cards:
            self.deck.remove(card)
        return cards

    def calculate_probabilities(self, hole_cards, community_cards=None):
        """
        Use probabilityValidator to get real probabilities (requiring hole cards)
        whenever community_cards is given.
        Returns a dictionary of handName -> probability (decimal form).
        """
        if community_cards:
            validator = probabilityValidator()
            raw_probs = validator.get_abbreviated_probabilities(hole_cards, community_cards)
            
            # Convert any keys to lowercase for front-end usage
            probabilities = {}
            for k, v in raw_probs.items():
                probabilities[k.lower()] = v

            return probabilities

        # If no community cards, return zero percentages or do your own logic:
        return {
            "pair": 0.0,
            "two pair": 0.0,
            "three of a kind": 0.0,
            "straight": 0.0,
            "flush": 0.0,
            "full house": 0.0,
            "four of a kind": 0.0,
            "straight flush": 0.0,
            "royal flush": 0.0
        }

    # def calculate_pre_flop_probabilities(self, probabilities={}, hole_cards):
    #     """Calculate probability of hitting a pair on the flop"""
    #     rank1, rank2 = hole_cards[0][0], hole_cards[1][0]
        
    #     if rank1 != rank2:
    #         num_outs = 6
    #         cum_prob = 1 
    #         for i in range(3):
    #             cum_prob *=  (52-len(hole_cards)- num_outs-i)/(52 - len(hole_cards)-i)
    #         probabilities['Pair'] = round((1-cum_prob) * 100, 2)
    #     else:
    #         probabilities['Pair'] = 100 # 100% chance of a pair
        
    #     return probabilities

    def calculate_post_flop_probabilities(self, probabilities, hole_cards, community_cards):
        """Calculate probabilities of making hands by the river using at least one hole card"""
        hole_ranks = [card[0] for card in hole_cards]
        hole_suits = [card[1] for card in hole_cards]
        all_cards = hole_cards + community_cards
        current_ranks = [card[0] for card in all_cards]
        current_suits = [card[1] for card in all_cards]
        rank_counts = defaultdict(int)
        suit_counts = defaultdict(int)
        for rank in current_ranks:
            rank_counts[rank] += 1
        for suit in current_suits:
            suit_counts[suit] += 1
        # Pair calculation (only counting pairs using hole cards)
        unpaired_hole_cards = [rank for rank in hole_ranks if rank_counts[rank] == 1]
        if unpaired_hole_cards:
            num_outs = sum(1 for card in self.deck if card[0] in unpaired_hole_cards)
            cum_prob = 1
            for i in range(2):
                cum_prob *= (47 - num_outs - i)/(47 - i)
            probabilities['Pair'] = round((1 - cum_prob) * 100, 2)
        
        # Three of a kind calculation (when we have a pair using hole cards)
        paired_hole_ranks = [rank for rank in hole_ranks if rank_counts[rank] == 2 
                            and sum(1 for card in hole_cards if card[0] == rank) > 0]
        if paired_hole_ranks:
            paired_rank = paired_hole_ranks[0]
            num_outs = sum(1 for card in self.deck if card[0] == paired_rank)
            cum_prob = 1
            for i in range(2):
                cum_prob *= (47 - num_outs - i)/(47 - i)
            probabilities['Three of a Kind'] = round((1 - cum_prob) * 100, 2)
        
        # Flush calculation (only when using at least one hole card)
        for hole_suit in hole_suits:
            suit_count = suit_counts[hole_suit]
            if suit_count == 4:  # Need one more for flush
                num_outs = sum(1 for card in self.deck if card[1] == hole_suit)
                cum_prob = 1
                for i in range(2):
                    cum_prob *= (47 - num_outs - i)/(47 - i)
                probabilities['Flush'] = round((1 - cum_prob) * 100, 2)
                break
        
        # Straight calculation (only counting straights using at least one hole card)
        straight_outs = self.count_straight_outs_post_flop(all_cards, hole_cards)
        if straight_outs > 0:
            # Calculate probability of hitting at least one of the needed cards
            # Probability of hitting at least one of the outs in two draws
            prob_hitting_one = 1 - ((47 - straight_outs) / 47) * ((46 - straight_outs) / 46)
            probabilities['Straight'] = round(prob_hitting_one * 100, 2)
        return probabilities

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

    def count_straight_outs_post_flop(self, all_cards, hole_cards):
        """Count straight outs after the flop, requiring at least one hole card"""
        ranks = sorted([self.rank_values[card[0]] for card in all_cards])
        hole_ranks = [self.rank_values[card[0]] for card in hole_cards]
        needed_ranks = set()
        
        # For each hole card
        for hole_rank in hole_ranks:
            # Look for possible straights using this hole card
            # Check each possible 5-card window that could make a straight
            for i in range(max(0, min(ranks) - 4), max(ranks) + 1):
                window = list(range(i, i + 5))
                if hole_rank in window:  # Our hole card is in this window
                    existing_ranks = set(ranks) & set(window)
                    if len(existing_ranks) >= 3:  # We have at least 3 cards of the straight
                        needed_ranks.update(set(window) - existing_ranks)
        
        # Count total outs, including duplicates for cards that complete multiple straights
        total_outs = 0
        for rank in needed_ranks:
            total_outs += sum(1 for card in self.deck if self.rank_values[card[0]] == rank)
        
        return total_outs

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
            if stage == 'exit':
                self.show_summary()
                return False
            if stage in ['pre', 'post']:
                break
            print("Please enter 'pre' or 'post' (or 'exit' to end)")

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
                        guess = input(f"\nWhat is the probability (in %) of making a {hand} by the river? (or 'exit' to end) ")
                        if guess.lower() == 'exit':
                            self.show_summary()
                            return False
                        
                        guess = float(guess)
                        difference = abs(guess - actual_prob)
                        self.total_questions += 1
                        
                        print(f"The actual probability is {actual_prob}%")
                        if difference <= 2:
                            print("Excellent! Within 2% of the actual probability.")
                            self.correct_answers += 1
                        else:
                            print("Keep practicing! That was off by more than 2%.")
                        break
                    except ValueError:
                        print("Please enter a valid number or 'exit'")
        return True

    def show_summary(self):
        """Show the final performance summary"""
        if self.total_questions > 0:
            accuracy = (self.correct_answers / self.total_questions) * 100
            print("\n=== Final Summary ===")
            print(f"Total questions answered: {self.total_questions}")
            print(f"Correct answers (within 2%): {self.correct_answers}")
            print(f"Accuracy: {accuracy:.1f}%")
        else:
            print("\nNo questions were answered.")

    def deal_new_hand(self):
        """Deal a new hand of poker with hole cards and community cards"""
        # Reset and shuffle deck
        self.deck = [[rank, suit] for rank in self.ranks for suit in self.suits]
        random.shuffle(self.deck)
        
        # Deal 2 hole cards
        hole_cards = [self.deck.pop() for _ in range(2)]
        
        # Deal 3 community cards (flop)
        community_cards = [self.deck.pop() for _ in range(3)]
        
        return hole_cards, community_cards

def display_card(card):
    """Display a card in a visually appealing format"""
    rank, suit = card
    return f"[{rank}{suit}]"

def display_hand(hole_cards, community_cards=None):
    """Display the hole cards and community cards with clear separation"""
    print("\n" + "="*30)
    print("=== New Hand Dealt ===")
    print("="*30)
    
    hole_cards_display = ' '.join(display_card(card) for card in hole_cards)
    print(f"\nYour cards: {hole_cards_display}")
    
    if community_cards:
        community_cards_display = ' '.join(display_card(card) for card in community_cards)
        print(f"Flop: {community_cards_display}")
    print("="*30)

def main():
    quiz = PokerQuiz()
    # validator = MonteCarloValidator()
    
    print("\n=== Poker Probability Quiz ===")
    print("Note: hands use at least one hole card.")

    stage = 'post'
    
    while True:
        hole_cards = quiz.deal_cards(2)
        community_cards = quiz.deal_cards(3) if stage == 'post' else None
        
        display_hand(hole_cards, community_cards)

        # validator._has_hand(hole_cards, community_cards)
        
        actual_probabilities = quiz.calculate_probabilities(hole_cards, community_cards)
        
        for hand, actual_prob in actual_probabilities.items():
            if actual_prob > 0:  # Only quiz on possible hands
                while True:
                    try:
                        print(f"\n--- {hand} ---")
                        guess = input(f"Probability (%) of {hand} by river? ('exit' to end): ")
                        if guess.lower() == 'exit':
                            quiz.show_summary()
                            return
                        
                        guess = float(guess)
                        difference = abs(guess - actual_prob)
                        quiz.total_questions += 1
                        
                        print(f"Actual: {actual_prob}%")
                        if difference <= 2:
                            print("Correct! Within 2%.")
                            quiz.correct_answers += 1
                        else:
                            print("Off by more than 2%.")
                        break
                    except ValueError:
                        print("Enter a number or 'exit'")

if __name__ == "__main__":
    main() 