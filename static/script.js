console.log("Script loaded"); // This should appear in the console when the script loads

document.addEventListener('DOMContentLoaded', function() {
    // Check if we are on the poker_probability_quiz page
    if (window.location.pathname === '/poker_probability_quiz') {
        console.log("On poker_probability_quiz page"); // Log to confirm we're on the right page

        const checkAnswerButton = document.getElementById('check-answer');
        const newHandButton = document.getElementById('new-hand');
        const communityCardsContainer = document.getElementById('community-cards');
        const holeCardsContainer = document.getElementById('hole-cards');
        const handOptionsContainer = document.getElementById('hand-options');

        // Check if the buttons exist before adding event listeners
        if (checkAnswerButton) {
            console.log("Check Answer button found"); // Debugging log
            checkAnswerButton.addEventListener('click', function() {
                console.log("Check Answers button clicked!"); // Debugging log
                // Add your answer checking logic here
            });
        } else {
            console.error("Element with ID 'check-answer' not found.");
        }

        if (newHandButton) {
            console.log("New Hand button found"); // Debugging log
            newHandButton.addEventListener('click', function() {
                console.log("Deal New Hand button clicked!"); // Debugging log
                renderCards(); // Call the function to render new cards
            });
        } else {
            console.error("Element with ID 'new-hand' not found.");
        }

        // Function to render cards
        function renderCards() {
            // Check if the containers exist before trying to set innerHTML
            if (communityCardsContainer) {
                communityCardsContainer.innerHTML = ''; // Clear existing cards
                const communityCards = ['A♠', 'K♣', 'Q♦']; // Example cards
                communityCards.forEach(card => {
                    const cardElement = document.createElement('div');
                    cardElement.className = 'card';
                    cardElement.textContent = card;
                    communityCardsContainer.appendChild(cardElement);
                });
            } else {
                console.error("Element with ID 'community-cards' not found.");
            }

            if (holeCardsContainer) {
                holeCardsContainer.innerHTML = ''; // Clear existing cards
                const holeCards = ['10♠', 'J♣']; // Example cards
                holeCards.forEach(card => {
                    const cardElement = document.createElement('div');
                    cardElement.className = 'card';
                    cardElement.textContent = card;
                    holeCardsContainer.appendChild(cardElement);
                });
            } else {
                console.error("Element with ID 'hole-cards' not found.");
            }

            if (handOptionsContainer) {
                handOptionsContainer.innerHTML = ''; // Clear existing options
                const handOptions = ['Flush', 'Straight', 'Full House']; // Example options
                handOptions.forEach(option => {
                    const optionElement = document.createElement('div');
                    optionElement.className = 'hand-option';
                    optionElement.textContent = option;
                    handOptionsContainer.appendChild(optionElement);
                });
            } else {
                console.error("Element with ID 'hand-options' not found.");
            }

            console.log("Rendering new cards...");
        }

        // Call the render function to display the initial game state
        renderCards();
    }

    // Check if we are on the home page
    if (window.location.pathname === '/') {
        const playQuizButton = document.getElementById('play-quiz'); // Assuming this is the ID of your button

        if (playQuizButton) {
            playQuizButton.addEventListener('click', function() {
                console.log("Play Quiz button clicked!"); // Debugging log
                window.location.href = '/poker_probability_quiz'; // Navigate to the quiz page
            });
        } else {
            console.error("Element with ID 'play-quiz' not found on the home page.");
        }
    }
});
