from flask import Flask, render_template, jsonify, request
from probability_puzzles import PokerQuiz

app = Flask(__name__, template_folder='templates')
quiz = PokerQuiz()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/poker_probability_quiz')
def poker_probability_quiz():
    return render_template('poker_probability_quiz.html')

@app.route('/new_hand', methods=['POST'])
def new_hand():
    # Generate a new hand
    hole_cards, community_cards = quiz.deal_new_hand()
    probabilities = quiz.calculate_probabilities(hole_cards, community_cards)
    
    return jsonify({
        'hole_cards': format_cards(hole_cards),
        'community_cards': format_cards(community_cards),
        'probabilities': probabilities
    })

def format_cards(cards):
    # Cards are already in correct format, just combine rank and suit
    return [f"{card[0]}{card[1]}" for card in cards]

if __name__ == '__main__':
    app.run(debug=True)