const question = document.getElementById('question');
const choices = Array.from(document.getElementsByClassName('choice-text'));
const test = document.getElementById('test');
let currentQuestion = {};
let acceptingAnswers = false;
let questionCounter = 0;
let availableQuestions = [];

let questions = [];

let answers = [];

fetch("static/data/questions.json")
    .then(res => {
        return res.json();
    })
    .then(loadedQuestions => {
        // console.log(loadedQuestions);
        questions = loadedQuestions;
        startGame();
    })
    .catch(err => {
        console.error(err);
    });

const MAX_QUESTIONS = 14;

startGame = () => {
    questionCounter = 0;
    availableQuestions = [...questions];
    getNewQuestion();
    test.classList.remove('hidden');
};

getNewQuestion = () => {
    if (availableQuestions.length === 0) {
        // return window.location.assign('profile');
    }

    if(questionCounter >= MAX_QUESTIONS){
        document.getElementById('loader').style.display = "block"
        fetch('/save_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ data: answers })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // alert(data.message);
                location.href="/output?output="+data.message
            } else {
                alert("Something went wrong")
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
        
    }
    questionCounter++;
    
    const questionIndex = Math.floor(0 * availableQuestions.length);
    currentQuestion = availableQuestions[questionIndex];
    question.innerHTML = currentQuestion.question;

    choices.forEach((choice) => {
        const number = choice.dataset['number'];
        choice.innerHTML = currentQuestion['choice' + number];
    });

    availableQuestions.splice(questionIndex, 1);
    acceptingAnswers = true;
};

choices.forEach((choice) => {
    choice.addEventListener('click', (e) => {
        if (!acceptingAnswers) return;

        acceptingAnswers = false;
        const selectedChoice = e.target;
        const selectedAnswer = selectedChoice.dataset['number'];

        selectedChoice.classList.add('selected-choice');
        answers.push(selectedAnswer)

        setTimeout(() => {
            selectedChoice.classList.remove('selected-choice');
            getNewQuestion();
        }, 1000);
    });
});

