import random
from collections import defaultdict
from probability_puzzles import PokerQuiz

class MonteCarloValidator:
    def __init__(self, num_simulations=100000):
        self.quiz = PokerQuiz()
        self.num_simulations = num_simulations
    def simulate_post_flop(self, hole_cards, community_cards=None):
        """Run Monte Carlo simulation and return probabilities for all hand types"""
        hand_types = ["Pair", "Two Pair", "Three of a Kind", "Straight", 
                     "Flush", "Full House", "Four of a Kind"]
        successes = {hand: 0 for hand in hand_types}
        
        for _ in range(self.num_simulations):
            # Reset deck and remove hole cards
            deck = [(rank, suit) for rank in self.quiz.ranks for suit in self.quiz.suits]
            for card in hole_cards:
                deck.remove(card)
            
            # Remove community cards if present
            if community_cards:
                for card in community_cards:
                    if card in deck:  # Check to avoid error if card was already removed
                        deck.remove(card)
            
            # Deal flop (or remaining community cards)
            num_to_deal = 5 - len(community_cards) if community_cards else 3
            flop = random.sample(deck, num_to_deal)
            all_cards = hole_cards + (community_cards if community_cards else []) + flop
            
            # Check each hand type
            for hand_type in hand_types:
                if self._has_hand(all_cards, hand_type):
                    successes[hand_type] += 1
        
        # Convert to percentages
        probabilities = {hand: (count / self.num_simulations) * 100 
                        for hand, count in successes.items()}
        
        return probabilities

    def _has_hand(self, cards, target_hand):
        """Check if the given cards make the target hand using at least one hole card"""
        # Separate hole cards (first 2) from other cards
        hole_cards = cards[:2]
        all_cards = cards
        
        ranks = [card[0] for card in all_cards]
        suits = [card[1] for card in all_cards]
        rank_counts = defaultdict(int)
        suit_counts = defaultdict(int)
        
        # Count ranks and suits
        for rank in ranks:
            rank_counts[rank] += 1
        for suit in suits:
            suit_counts[suit] += 1
        
        # Count hole card ranks and suits separately
        hole_ranks = [card[0] for card in hole_cards]
        hole_suits = [card[1] for card in hole_cards]
        
        # Convert face cards to numbers for straight checking
        numeric_ranks = []
        for rank in ranks:
            if rank == 'A':
                numeric_ranks.append(14)  # Ace high
                numeric_ranks.append(1)   # Ace low for A-5 straight
            elif rank == 'K':
                numeric_ranks.append(13)
            elif rank == 'Q':
                numeric_ranks.append(12)
            elif rank == 'J':
                numeric_ranks.append(11)
            else:
                numeric_ranks.append(int(rank))
        
        numeric_ranks = sorted(list(set(numeric_ranks)))  # Remove duplicates and sort
        
        if target_hand == "Pair":
            # Check if there's a pair AND at least one hole card is part of any pair
            pairs_exist = any(count >= 2 for count in rank_counts.values())
            uses_hole_card = any(rank_counts[rank] >= 2 for rank in hole_ranks)
            return pairs_exist and uses_hole_card
        
        elif target_hand == "Two Pair":
            # Count total pairs and pairs involving hole cards
            total_pairs = sum(1 for count in rank_counts.values() if count >= 2)
            uses_hole_card = any(rank_counts[rank] >= 2 for rank in hole_ranks)
            return total_pairs >= 2 and uses_hole_card
        
        elif target_hand == "Three of a Kind":
            # Check if there's a three of a kind AND at least one hole card is part of it
            three_exists = any(count >= 3 for count in rank_counts.values())
            uses_hole_card = any(rank_counts[rank] >= 3 for rank in hole_ranks)
            return three_exists and uses_hole_card
        
        elif target_hand == "Straight":
            # First, find if there's a straight
            has_straight = False
            straight_cards = []
            for i in range(len(numeric_ranks) - 4):
                if numeric_ranks[i+4] - numeric_ranks[i] == 4:
                    straight_cards = numeric_ranks[i:i+5]
                    has_straight = True
                    break
            
            if not has_straight:
                return False
            
            # Convert hole cards to numeric values
            numeric_hole_ranks = []
            for rank in hole_ranks:
                if rank == 'A':
                    numeric_hole_ranks.extend([1, 14])
                elif rank == 'K':
                    numeric_hole_ranks.append(13)
                elif rank == 'Q':
                    numeric_hole_ranks.append(12)
                elif rank == 'J':
                    numeric_hole_ranks.append(11)
                else:
                    numeric_hole_ranks.append(int(rank))
            
            # Check if any hole card is part of the straight
            return any(rank in straight_cards for rank in numeric_hole_ranks)
        
        elif target_hand == "Flush":
            # Check if there's a flush AND at least one hole card is part of it
            for suit in set(suits):
                if suit_counts[suit] >= 5:
                    # Check if at least one hole card is part of this flush
                    hole_cards_in_flush = sum(1 for card in hole_cards if card[1] == suit)
                    if hole_cards_in_flush > 0:
                        return True
            return False
        
        elif target_hand == "Full House":
            # Find three of a kind that uses a hole card
            three_of_a_kind_rank = None
            for rank in hole_ranks:
                if rank_counts[rank] >= 3:
                    three_of_a_kind_rank = rank
                    break
            
            if not three_of_a_kind_rank:
                return False
            
            # Check for any pair (can be from any cards) different from the three of a kind
            for rank, count in rank_counts.items():
                if rank != three_of_a_kind_rank and count >= 2:
                    return True
            return False
        
        elif target_hand == "Four of a Kind":
            # Check if there's a four of a kind AND at least one hole card is part of it
            for rank, count in rank_counts.items():
                if count >= 4 and rank in hole_ranks:
                    return True
            return False
        
        return False

def run_validation_tests():
    validator = MonteCarloValidator()
    
    # Test cases
    # PAIR Test Cases
    test_cases = [
        {
            "hole_cards": [('A', '♠'), ('A', '♥')],
            "community_cards": [('K', '♦'), ('Q', '♣'), ('J', '♥')],
            "stage": "post-flop"
        },
        {
            "hole_cards": [('A', '♠'), ('K', '♠')],
            "community_cards": [('Q', '♠'), ('J', '♠'), ('2', '♣')],
            "stage": "post-flop"
        },
        {
            "hole_cards": [('8', '♣'), ('8', '♥')],
            "community_cards": [('9', '♠'), ('A', '♣'), ('K', '♦')],
            "stage": "post-flop"
        },
        {
            "hole_cards": [('J', '♣'), ('10', '♥')],
            "community_cards": [('9', '♠'), ('8', '♣'), ('2', '♦')],
            "stage": "post-flop"
        },
        {
            "hole_cards": [('A', '♣'), ('A', '♥')],
            "community_cards": [('A', '♦'), ('A', '♠'), ('K', '♣')],
            "stage": "post-flop"
        },
        {
            "hole_cards": [('K', '♣'), ('K', '♥')],
            "community_cards": [('K', '♦'), ('Q', '♠'), ('Q', '♣')],
            "stage": "post-flop"
        },
        {
            "hole_cards": [('Q', '♣'), ('J', '♣')],
            "community_cards": [('Q', '♥'), ('J', '♠'), ('2', '♦')],
            "stage": "post-flop"
        },
    ]
    
    for test in test_cases:
        hole_cards = test["hole_cards"]
        community_cards = test["community_cards"]
        
        # Get Monte Carlo probability
        mc_prob = validator.simulate_post_flop(hole_cards, community_cards)
        
        print(f"\nTest Case: {hole_cards} + {community_cards}")
        print(f"Monte Carlo Probabilities:")
        for hand, prob in mc_prob.items():
            print(f"  {hand}: {prob:.2f}%")

if __name__ == "__main__":
    # run_validation_tests()
    validator = MonteCarloValidator()
    # hole_cards = [('5', '♠'), ('Q', '♥')]
    # community_cards = [('2', '♦'), ('4', '♣'), ('3', '♥')]
    # mc_prob = validator.simulate_post_flop(hole_cards, community_cards)
    # print(f"\nTest Case: {hole_cards} + {community_cards}")
    # print(f"Monte Carlo Probabilities:")
    # for hand, prob in mc_prob.items():
    #     print(f"  {hand}: {prob:.2f}%")

    pair_test_cases = {'hole_pair':
        # already has pair
        {
            "hole_cards": [('A', '♠'), ('A', '♥')],
            "community_cards": [('K', '♦'), ('Q', '♣'), ('J', '♥')],
            "stage": "post-flop"
        }
    ,
        # pair from flop + hole card
        'pair_from_flop':
        {
            "hole_cards": [('A', '♠'), ('7', '♥')],
            "community_cards": [('K', '♦'), ('Q', '♣'), ('7', '♥')],
            "stage": "post-flop"
        },
        # no pair
        'no_pair':
        {
            "hole_cards": [('A', '♠'), ('7', '♥')],
            "community_cards": [('K', '♦'), ('Q', '♣'), ('J', '♥')],
            "stage": "post-flop"
        },
    }
    pair_probabilities = {}
    for scenario in pair_test_cases:
        mc_prob = validator.simulate_post_flop(pair_test_cases[scenario]["hole_cards"], pair_test_cases[scenario]["community_cards"])
        pair_probabilities[scenario] = mc_prob['Pair']
    print(pair_probabilities)