from flask import Flask, render_template, jsonify, request, session
from probability_puzzles import PokerQuiz
# from flask_session import Session  # If you want to use server-side sessions

app = Flask(__name__, template_folder='templates')
app.secret_key = 'REPLACE_WITH_RANDOM_KEY'  # needed for session
# app.config['SESSION_TYPE'] = 'filesystem'  # example
# Session(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/poker_probability_quiz')
def poker_probability_quiz():
    return render_template('poker_probability_quiz.html')

########################################################################
# Deal a new hand and store the associated probabilities in session
########################################################################
@app.route('/new_hand', methods=['POST'])
def new_hand():
    pq = PokerQuiz()
    hole_cards, community_cards = pq.deal_new_hand()
    
    # This calls your existing method, which uses the validator if community_cards is given.
    probabilities = pq.calculate_probabilities(hole_cards, community_cards)

    # Save everything in session
    session['current_hole_cards'] = hole_cards
    session['current_community_cards'] = community_cards
    session['current_probabilities'] = probabilities

    return jsonify({
        'hole_cards': format_cards(hole_cards),
        'community_cards': format_cards(community_cards),
        'probabilities': probabilities
    })

########################################################################
# Render the main quiz page
########################################################################
@app.route("/poker_quiz")
def poker_quiz():
    """
    Render the poker_probability_quiz UI that we want to connect to the backend quiz logic.
    """
    return render_template("poker_probability_quiz.html")

########################################################################
# Example dealing route we had before; can remove if redundant
########################################################################
@app.route("/poker_quiz/deal", methods=["POST"])
def poker_quiz_deal():
    """
    Optional older route – if you prefer the same logic as /new_hand, 
    you can unify or remove this.
    """
    pq = PokerQuiz()
    hole_cards, community_cards = pq.deal_new_hand()
    hole_strs = [f"{card[0]}{card[1]}" for card in hole_cards]
    flop_strs = [f"{card[0]}{card[1]}" for card in community_cards]
    return jsonify({"hole": hole_strs, "flop": flop_strs})

########################################################################
# (Optional) A route to "start" or "reset" a quiz session
########################################################################
@app.route("/poker_quiz/start", methods=["POST"])
def poker_quiz_start():
    session['quiz'] = {
        'hole_cards': [],
        'community_cards': [],
        'correct_answers': 0,
        'total_questions': 0,
        'stage': 'post'
    }
    # If you want to deal immediately:
    pq = PokerQuiz()
    hole_cards = pq.deal_cards(2)
    community_cards = pq.deal_cards(3)
    # store in session
    session['quiz']['hole_cards'] = hole_cards
    session['quiz']['community_cards'] = community_cards
    probabilities = pq.calculate_probabilities(hole_cards, community_cards)
    session['quiz']['probabilities'] = probabilities

    return jsonify({
        "hole": [f"{c[0]}{c[1]}" for c in hole_cards],
        "flop": [f"{c[0]}{c[1]}" for c in community_cards],
        "stage": session['quiz']['stage']
    })

########################################################################
# Check multiple guesses at once, using the probabilities from session
########################################################################
@app.route("/poker_quiz/check_all", methods=["POST"])
def poker_quiz_check_all():
    data = request.json or {}
    all_guesses = data.get("guesses", {})
    stored_probs = session.get('current_probabilities', {})  # We do not overwrite them

    results = {}
    for hand_type, guessed_prob in all_guesses.items():
        # The dictionary from your validator is presumably decimal probabilities:
        # e.g.: {"pair": 0.18, "two pair": 0.07, ...}
        actual_decimal = stored_probs.get(hand_type.lower(), 0.0)
        actual_percent = actual_decimal 
        difference = abs(guessed_prob - actual_percent)
        correct = (difference <= 5.0)
        results[hand_type] = {"actual_prob": actual_percent, "correct": correct}

    # Keep track of quiz stats if you like
    quiz_data = session.get('quiz', {})
    quiz_data['total_questions'] = quiz_data.get('total_questions', 0) + len(all_guesses)
    newly_correct = sum(1 for info in results.values() if info["correct"])
    quiz_data['correct_answers'] = quiz_data.get('correct_answers', 0) + newly_correct
    session['quiz'] = quiz_data

    return jsonify({
        "results": results,
        "correct_answers": quiz_data.get("correct_answers", 0),
        "total_questions": quiz_data.get("total_questions", 0)
    })

@app.route("/exit_quiz", methods=["POST"])
def exit_quiz():
    """
    Clear session and return JSON instructing front-end to go home.
    """
    session.clear()
    return jsonify({"redirect": "/"})

def format_cards(cards):
    # Cards are already in correct format, just combine rank and suit
    return [f"{card[0]}{card[1]}" for card in cards]

if __name__ == '__main__':
    app.run(debug=True)