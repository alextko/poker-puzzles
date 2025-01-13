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
        self.correct_answers = 0
        self.total_questions = 0
    
    def deal_cards(self, num_cards):
        """Deal specified number of cards"""
        cards = random.sample(self.deck, num_cards)
        for card in cards:
            self.deck.remove(card)
        return cards

    def calculate_probabilities(self, hole_cards, community_cards=None):
        """Calculate probabilities for different poker hands given any game state"""
        probabilities = {}
        
        # Reset deck and remove known cards
        self.deck = [(rank, suit) for rank in self.ranks for suit in self.suits]
        for card in hole_cards:
            self.deck.remove(card)
        if community_cards:
            for card in community_cards:
                self.deck.remove(card)

        all_cards = hole_cards + (community_cards if community_cards else [])
        current_ranks = [card[0] for card in all_cards]
        current_suits = [card[1] for card in all_cards]
        rank_counts = defaultdict(int)
        suit_counts = defaultdict(int)
        for rank in current_ranks:
            rank_counts[rank] += 1
        for suit in current_suits:
            suit_counts[suit] += 1

        # Determine the stage of the game
        num_community_cards = len(community_cards) if community_cards else 0
        if num_community_cards == 0:
            self.calculate_pre_flop_probabilities(probabilities, hole_cards)
        elif num_community_cards in [3, 4, 5]:
            self.calculate_post_flop_probabilities(probabilities, all_cards, rank_counts, suit_counts, num_community_cards)
        
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

    def calculate_post_flop_probabilities(self, probabilities, all_cards, rank_counts, suit_counts, num_community_cards):
        """Calculate probabilities of making hands by the river using at least one hole card"""
        hole_cards = all_cards[:2]  # First two cards are hole cards
        hole_ranks = [card[0] for card in hole_cards]
        hole_suits = [card[1] for card in hole_cards]
        
        # Pair calculation (only counting pairs using hole cards)
        unpaired_hole_cards = [rank for rank in hole_ranks if rank_counts[rank] == 1]
        if unpaired_hole_cards:
            num_outs = sum(1 for card in self.deck if card[0] in unpaired_hole_cards)
            cum_prob = 1
            for i in range(5 - num_community_cards):
                cum_prob *= (47 - num_outs - i)/(47 - i)
            probabilities['Pair'] = round((1 - cum_prob) * 100, 2)
        
        # Three of a kind calculation (when we have a pair using hole cards)
        paired_hole_ranks = [rank for rank in hole_ranks if rank_counts[rank] == 2 
                            and sum(1 for card in hole_cards if card[0] == rank) > 0]
        if paired_hole_ranks:
            paired_rank = paired_hole_ranks[0]
            num_outs = sum(1 for card in self.deck if card[0] == paired_rank)
            cum_prob = 1
            for i in range(5 - num_community_cards):
                cum_prob *= (47 - num_outs - i)/(47 - i)
            probabilities['Three of a Kind'] = round((1 - cum_prob) * 100, 2)
        
        # Flush calculation (only when using at least one hole card)
        for hole_suit in hole_suits:
            suit_count = suit_counts[hole_suit]
            if suit_count >= 4:  # Need one more for flush
                num_outs = sum(1 for card in self.deck if card[1] == hole_suit)
                cum_prob = 1
                for i in range(5 - num_community_cards):
                    cum_prob *= (47 - num_outs - i)/(47 - i)
                probabilities['Flush'] = round((1 - cum_prob) * 100, 2)
                break
        
        # Straight calculation (only counting straights using at least one hole card)
        straight_outs = self.count_straight_outs_post_flop(all_cards, hole_cards)
        if straight_outs > 0:
            cum_prob = 1
            for i in range(5 - num_community_cards):
                cum_prob *= (47 - straight_outs - i)/(47 - i)
            probabilities['Straight'] = round((1 - cum_prob) * 100, 2)

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
                        
                        print(f"Actual: {actual_prob}%")
                        if difference <= 2:
                            print("Correct! Within 2%.")
                            self.correct_answers += 1
                        else:
                            print("Off by more than 2%.")
                        break
                    except ValueError:
                        print("Enter a number or 'exit'")
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
    
    print("\n=== Poker Probability Quiz ===")
    print("Note: Probabilities use at least one hole card.")
    
    # Ask for game mode once at the start
    while True:
        stage = input("\nQuiz mode (pre/post): ").lower()
        if stage in ['pre', 'post']:
            break
        print("Enter 'pre' or 'post'")
    
    while True:
        hole_cards = quiz.deal_cards(2)
        community_cards = quiz.deal_cards(3) if stage == 'post' else None
        
        display_hand(hole_cards, community_cards)
        
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