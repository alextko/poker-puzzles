import random

# If you have a separate module for evaluating the best poker hand,
# import it here (e.g. from hand_categorizor import categorize_hand).
# We'll leave a placeholder method below, but replace it with your real logic.

# 1) IMPORT from validator.py
from validator import HandEvaluator  # or the real name of your validator class/function

class NameTheHandGame:
    def __init__(self):
        """
        Initialize ranks, suits, and a fresh deck of cards.
        This structure mimics the style used in probability_puzzles.py.
        """
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.suits = ['♠', '♥', '♦', '♣']
        # Build the deck: a list of [rank, suit]
        self.deck = [[rank, suit] for rank in self.ranks for suit in self.suits]
        # Shuffle once at initialization
        random.shuffle(self.deck)
        
        self.correct_answers = 0
        self.total_questions = 0
        
        # All possible hand options in textual form
        self.hand_options = [
            "High Card",
            "Pair",
            "Two Pair",
            "Three of a Kind",
            "Straight",
            "Flush",
            "Full House",
            "Four of a Kind",
            "Straight Flush",
            "Royal Flush"
        ]

    def deal_cards(self, num_cards):
        """
        Deal 'num_cards' from the deck, removing them so they can't be re-dealt.
        """
        dealt = self.deck[:num_cards]
        self.deck = self.deck[num_cards:]
        return dealt

    def reset_deck(self):
        """
        Optionally reset and shuffle deck if you want to start a new round from a fresh deck.
        """
        self.deck = [[rank, suit] for rank in self.ranks for suit in self.suits]
        random.shuffle(self.deck)

    def identify_best_hand(self, hole_cards, community_cards):
        """
        Call the validator to find the best hand from these 7 cards.
        Make sure the returned hand name matches an item in self.hand_options.
        """
        # 2) USE the validator to identify the best hand
        evaluator = HandEvaluator()  # or however you instantiate your validator
        best_hand = evaluator.identify_best_hand(hole_cards, community_cards)
        # For example, if 'best_hand' is "Four of a Kind", that should match one of self.hand_options

        return best_hand

    def name_that_hand(self):
        """
        Core logic for the "Name the Hand" game.
        1) Deal 2 hole cards + 5 community cards.
        2) Show them to the player (console-based).
        3) Prompt them to guess the best hand from the available options.
        4) Compare with identify_best_hand() to see if the guess is correct.
        5) Track stats and repeat or exit.
        """
        hole_cards = self.deal_cards(2)
        community_cards = self.deal_cards(5)

        # Display the cards to the console
        print("\nYour Hole Cards:")
        for c in hole_cards:
            print(f"{c[0]}{c[1]}", end=" ")
        print("\n\nCommunity Cards:")
        for c in community_cards:
            print(f"{c[0]}{c[1]}", end=" ")
        print("\n")

        # Let the user pick from the known hand options
        for idx, opt in enumerate(self.hand_options, start=1):
            print(f"{idx}. {opt}")
        
        choice = input("\nWhich hand do you think you have? Enter a number or type 'exit': ")
        if choice.lower() == 'exit':
            return False  # user wants to exit

        try:
            choice_idx = int(choice)
            if choice_idx < 1 or choice_idx > len(self.hand_options):
                raise ValueError
            user_guess = self.hand_options[choice_idx - 1]
        except ValueError:
            print("Invalid choice. Please pick a valid number.")
            return True

        # Identify the correct best hand
        correct_hand = self.identify_best_hand(hole_cards, community_cards)

        # Update stats
        self.total_questions += 1
        if user_guess == correct_hand:
            print(f"Correct! The best hand is indeed {correct_hand}.")
            self.correct_answers += 1
        else:
            print(f"Not quite. The best hand is {correct_hand}.")

        # Show running stats
        accuracy = (self.correct_answers / self.total_questions) * 100
        print(f"\n===== Stats so far =====")
        print(f"Questions asked: {self.total_questions}")
        print(f"Correct answers: {self.correct_answers}")
        print(f"Accuracy: {accuracy:.2f}%")

        return True

    def run(self):
        """
        Run the Name the Hand game in a loop until the user decides to exit.
        """
        print("\n=== Welcome to 'Name the Hand' ===")
        while True:
            continue_game = self.name_that_hand()
            if not continue_game:  # user typed 'exit' or something
                break
            # Optionally reset deck each round if you prefer:
            self.reset_deck()

        # Final summary on exit
        if self.total_questions > 0:
            accuracy = (self.correct_answers / self.total_questions) * 100
            print("\n===== Final Summary =====")
            print(f"Questions asked: {self.total_questions}")
            print(f"Correct answers: {self.correct_answers}")
            print(f"Accuracy: {accuracy:.2f}%")
        else:
            print("\nNo questions answered. Thanks for playing!")

# ─────────────────────────────────────────────────────────────────────────
# ADD THIS MAIN GUARD to run from terminal with: python beginner_games.py
# ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game = NameTheHandGame()
    game.run()
