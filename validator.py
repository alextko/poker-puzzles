import random
from collections import defaultdict
from probability_puzzles import PokerQuiz

class MonteCarloValidator:
    def __init__(self, num_simulations=100000):
        self.quiz = PokerQuiz()
        self.num_simulations = num_simulations
    def simulate_pre_flop(self, hole_cards, target_hand):
        """Run Monte Carlo simulation for pre-flop scenarios"""
        successes = 0
        
        for _ in range(self.num_simulations):
            # Reset deck and remove hole cards
            deck = [(rank, suit) for rank in self.quiz.ranks for suit in self.quiz.suits]
            for card in hole_cards:
                deck.remove(card)
            
            # Deal flop
            flop = random.sample(deck, 3)
            all_cards = hole_cards + flop
            
            # Check if target hand is made
            if self._has_hand(all_cards, target_hand):
                successes += 1
        
        return (successes / self.num_simulations) * 100

    def _has_hand(self, cards, target_hand):
        """Check if the given cards make the target hand"""
        ranks = [card[0] for card in cards]
        rank_counts = defaultdict(int)
        for rank in ranks:
            rank_counts[rank] += 1
            
        if target_hand == "Pair":
            return max(rank_counts.values()) >= 2
        elif target_hand == "Three of a Kind":
            return max(rank_counts.values()) >= 3
        # Add more hand checks as needed
        
        return False

def run_validation_tests():
    validator = MonteCarloValidator()
    
    # Test cases
    test_cases = [
        {
            "hole_cards": [('A', '♠'), ('K', '♠')],
            "target_hand": "Pair",
            "stage": "pre-flop"
        },
        {
            "hole_cards": [('8', '♣'), ('8', '♥')],
            "target_hand": "Three of a Kind",
            "stage": "post-flop"
        },
        # Add more test cases here
    ]
    
    for test in test_cases:
        hole_cards = test["hole_cards"]
        target_hand = test["target_hand"]
        
        # Get probability from our calculator
        calc_prob = PokerQuiz().calculate_probabilities(hole_cards)[target_hand]
        
        # Get Monte Carlo probability
        mc_prob = validator.simulate_pre_flop(hole_cards, target_hand)
        
        print(f"\nTest Case: {hole_cards} -> {target_hand}")
        print(f"Calculator Probability: {calc_prob:.2f}%")
        print(f"Monte Carlo Probability: {mc_prob:.2f}%")
        print(f"Difference: {abs(calc_prob - mc_prob):.2f}%")

if __name__ == "__main__":
    # run_validation_tests()
    quiz = PokerQuiz()
    hole_cards = [('A', '♠'), ('K', '♠')]
    community_cards = [('A', '♠'), ('K', '♠'), ('Q', '♠')]
    probs = quiz.calculate_post_flop_probabilities(probabilities={}, hole_cards=hole_cards, community_cards=community_cards)
    print(probs)
