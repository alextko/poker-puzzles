import random
from collections import defaultdict
import pickle
import tqdm
import json
def binom(n, k):
    """Calculate n choose k (binomial coefficient)
    Args:
        n (int): Total number of items
        k (int): Number of items to choose
    Returns:
        int: Number of ways to choose k items from n items
    """
    if k > n:
        return 0
    if k == 0 or k == n:
        return 1
    
    # Use multiplicative formula
    result = 1
    for i in range(k):
        result *= (n - i)
        result //= (i + 1)
    return result

# def print_pretty_dict(data):
#     for hand, values in data.items():
#         print(f"{hand}:")
#         for key, value in values.items():
#             print(f"  {key}: {value}")
#         print()  # Add a blank line for better separation


class probabilityValidator:
    def __init__(self, num_simulations=10000):
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.suits = ['♠', '♥', '♦', '♣']
        self.deck = [[rank, suit] for rank in self.ranks for suit in self.suits]
        self.rank_values = {rank: idx for idx, rank in enumerate(self.ranks)}
        self.num_simulations = num_simulations
    def simulate_post_flop(self, hole_cards, community_cards=None):
        """Run Monte Carlo simulation and return probabilities for all hand types"""
        hand_types = ["Pair", "Two Pair", "Three of a Kind", "Straight", 
                     "Flush", "Full House", "Four of a Kind"]
        successes = {hand: 0 for hand in hand_types}
        
        for _ in tqdm.tqdm(range(self.num_simulations)):
            # Reset deck and remove hole cards
            deck = [[rank, suit] for rank in self.ranks for suit in self.suits]
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


   

    def _num_outs(self, hole_cards, community_cards, target_hand):
        if target_hand == "Two Pair":
            verbose = False
        else:
            verbose = False
        deck = [[rank, suit] for rank in self.ranks for suit in self.suits]
        for card in hole_cards + community_cards:
            if card in deck:
                deck.remove(card)
        outs = 0
        if len(community_cards) == 4:
            # Single card outs
            for potential_card in deck:
                all_cards = hole_cards + community_cards + [potential_card]
                if self._has_hand(all_cards, target_hand):
                    outs += 1
        else:
            two_card_outs = 0
            two_card_total = 0
            for card in deck:
                all_cards = hole_cards + community_cards + [card]
                if self._has_hand(all_cards, target_hand):
                    outs += 1
            for card in deck:
                for card2 in deck:
                    if card2 == card:
                        continue
                    two_card_total += 1
                    all_cards = hole_cards + community_cards + [card]
                    if self._has_hand(all_cards, target_hand):
                        continue
                    all_cards = hole_cards + community_cards + [card, card2]
                    if self._has_hand(all_cards, target_hand):
                        if verbose:
                            input([card,card2])
                        two_card_outs += 1
                # if not self._has_hand(all_cards, target_hand):
                #     for card2 in deck:
                #         if card2 == card:
                #             continue
                #         all_cards = hole_cards + community_cards + [card, card2]
                #         if self._has_hand(all_cards, target_hand):
                #             if verbose:
                #                 input([card, card2])

                #             outs += 1

        return {'outs': outs, 'two_card_outs': two_card_outs, 'two_card_total': two_card_total}

    def calculate_probability(self, hole_cards, community_cards):
        """Calculate outs for all possible hand improvements
        Returns:
            dict: Dictionary with keys as hand types and values as tuples (outs, probability)
        """
        hand_types = ["Pair", "Two Pair", "Three of a Kind", "Straight", 
                      "Flush", "Full House", "Four of a Kind"]

        outs_dict = {}
        current_cards = hole_cards + community_cards
        cards_needed = 1 if len(community_cards) == 4 else 2
        remaining_cards = 52 - len(current_cards)
        # print('remaining cards', remaining_cards)
        for hand_type in hand_types:
            if not self._has_hand(current_cards, hand_type):
                num_outs_info = self._num_outs(hole_cards, community_cards, hand_type)
                num_outs = num_outs_info['outs']
                if 'two_card_outs' in num_outs_info:
                    two_card_outs = num_outs_info['two_card_outs']
                    two_card_total = num_outs_info['two_card_total']
                # Calculate probability based on number of cards to come
                if cards_needed == 1:
                    # One card to come: outs / remaining cards
                    probability = (num_outs / remaining_cards) * 100
                else:
                    # Two cards to come using binomial probability:
                    # P(at least one out) = 1 - P(no outs)
                    # P(no outs) = (remaining_cards - outs) * (remaining_cards - outs - 1) / (remaining_cards * (remaining_cards - 1))
                    # no_outs_prob = ((remaining_cards - num_outs) * (remaining_cards - num_outs - 1)) / (remaining_cards * (remaining_cards - 1))
                    # probability = (1 - no_outs_prob) * 100
                    # no_outs_prob = binom(remaining_cards - num_outs)
                    fail_draws = binom(remaining_cards - num_outs, 2)
                    all_draws = binom(remaining_cards, 2)
                    probability_one = (1 - fail_draws / all_draws) * 100
                    probility_two = (two_card_outs / two_card_total) * 100
                    probability = (probability_one + probility_two)
                
                if 'two_card_outs' in num_outs_info:
                    outs_dict[hand_type] = {'outs': num_outs,
                      'two_card_outs': two_card_outs,'probability': round(probability, 2)}
                else:
                    outs_dict[hand_type] = (num_outs, round(probability, 2))
        return outs_dict

    def abbreviate_probability_dict(self, probability_dict):
        """
        Returns an abbreviated form of the probability dictionary,
        keeping only the hand names and their corresponding probability values.

        """
        # Create a new dictionary with only hand names and their probabilities
        abbreviated_dict = {}
        for key in probability_dict: 
            abbreviated_dict[key] = probability_dict[key]['probability']
        return abbreviated_dict

    def get_abbreviated_probabilities(self, hole_cards, community_cards):
        """
        Calculates the probabilities and returns an abbreviated dictionary.

        """
        probabilities = self.calculate_probability(hole_cards, community_cards)
        # input (probabilities)
        return self.abbreviate_probability_dict(probabilities)


def run_validation_tests():
    validator = probabilityValidator()

if __name__ == "__main__":
    # run_validation_tests()
    validator = probabilityValidator()
    # with open('test_scenarios.json', 'r') as f:
    #     test_scenarios = json.load(f)
    # all_probabilities = {}
    # for hand_type in test_scenarios:
    #     all_probabilities[hand_type] = {}
    #     for scenario in test_scenarios[hand_type]:
    #         mc_prob = validator.simulate_post_flop(test_scenarios[hand_type][scenario]["hole_cards"], test_scenarios[hand_type][scenario]["community_cards"])
    #         all_probabilities[hand_type][scenario] = mc_prob[hand_type]
    # print(all_probabilities)
    # pickle.dump(pair_probabilities, open('pair_probabilities.pickle', 'wb'))
    hole_cards =  [["A", "♠"], ["7", "♥"]]
    community_cards = [["K", "♦"], ["Q", "♣"], ["9", "♣"]]
    # probabilities = validator.calculate_probability(hole_cards, community_cards)
    # print_pretty_dict(probabilities)
    abbreviated_probabilities = validator.get_abbreviated_probabilities(hole_cards, community_cards)
    print(abbreviated_probabilities)
