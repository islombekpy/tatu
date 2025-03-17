
// function getCookie(name) {

//     return document.cookie.split('; ').find(row => row.startsWith(name + '='))
  
//         ?.split('=')[1];
  
//   }
  
//   const csrftoken = getCookie('csrftoken');
  
//   const questionElements = Array.from(document.querySelectorAll('.box.box-default.question'));
  
//   // Sahifadagi savollarni yig‘ish
  
//   const questionsAndAnswers = questionElements.map((questionEl, index) => ({
  
//     title: questionEl.querySelector('h3.box-title').textContent.trim(),
  
//     index: index
  
//   }));
  
//   // Backend-ga so‘rov yuborish
  
//   fetch("https://eea8-213-230-99-218.ngrok-free.app/api/search/", {
  
//     method: "POST",
  
//     body: JSON.stringify(questionsAndAnswers),
  
//     headers: {
  
//         "Content-type": "application/json; charset=UTF-8",
  
//         "X-CSRFToken": csrftoken
  
//     }
//   })
//   .then(response => response.json())
//   .then(data => {
//     questionElements.forEach((questionEl, index) => {
//         const answerObj = data?.[index]; // Agar mavjud bo'lmasa undefined qaytaradi
//         const answerText = answerObj && Array.isArray(answerObj.answer) 
//             ? answerObj.answer.join(", ") 
//             : "-"; 
//         const questionTextElement = questionEl.querySelector('h3.box-title');
//         const questionText = questionTextElement ? questionTextElement.textContent.trim() : "";
//         if (questionTextElement) {
//             // Javobni savol matniga tasodifiy joyda qo‘shish
//             const randomPosition = Math.floor(Math.random() * (questionText.length + 1));
//             questionTextElement.textContent = 
//                 questionText.slice(0, randomPosition) + 
//                 " (" + answerText + ") " + 
//                 questionText.slice(randomPosition);
//             questionEl.setAttribute("title", answerText);
//         }
//     });
//   })
  
// function getCookie(name) {
//   return document.cookie.split(`; ${name}=`).pop().split(';').shift();
// }

// const csrftoken = getCookie('csrftoken');
// const questionElements = Array.from(document.querySelectorAll('.box.box-default.question'));
// const questionsAndAnswers = questionElements.map((questionEl, index) => ({
//   question: questionEl.querySelector('h3.box-title').textContent.trim(),
//   index: index + 1,
//   answers: Array.from(questionEl.querySelectorAll('.box-body p .qv')).map(answerEl => answerEl.textContent.trim())
// }));

// fetch("https://fbd3-45-150-26-213.ngrok-free.app/api/search/", {
//   method: "POST",
//   body: JSON.stringify(questionsAndAnswers),
//   headers: {
//     "Content-type": "application/json; charset=UTF-8",
//     "X-CSRFToken": csrftoken
//   }
// })
// .then(response => {
//   if (!response.ok) throw new Error('Network response was not ok');
//   return response.json();
// })
// .then(data => {
//   questionElements.forEach((questionEl, index) => {
//     const answer = data[index]?.answer || "Javob topilmadi";
//     const questionTextElement = questionEl.querySelector('h3.box-title');
//     const questionText = questionTextElement.textContent.trim();
//     const randomPosition = Math.floor(Math.random() * (questionText.length + 1));
//     questionTextElement.textContent = questionText.slice(0, randomPosition) + answer + questionText.slice(randomPosition);
//     questionEl.setAttribute("title", answer);
//   });
// })
// .catch(error => console.error('Error:', error));


/**
 * Question Answer Integration - Improved Version
 * This script fetches answers for questions and inserts them into the page.
 */

// Safe cookie retrieval function


// Safe cookie retrieval function
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

// Configuration
const API_ENDPOINT = "https://fbd3-45-150-26-213.ngrok-free.app/api/search/";
const QUESTION_SELECTOR = '.box.box-default.question';
const QUESTION_TITLE_SELECTOR = 'h3.box-title';

// Main function to execute the script
function processQuestions() {
  try {
    // Get CSRF token for the request
    const csrftoken = getCookie('csrftoken');
    
    // Find all question elements on the page
    const questionElements = Array.from(document.querySelectorAll(QUESTION_SELECTOR));
    
    // If no questions found, exit early
    if (!questionElements.length) {
      console.info('No questions found on the page');
      return;
    }
    
    console.info(`Found ${questionElements.length} questions on the page`);
    
    // Extract just the questions
    const questions = questionElements.map(questionEl => {
      const titleElement = questionEl.querySelector(QUESTION_TITLE_SELECTOR);
      if (!titleElement) return null;
      
      const questionText = titleElement.textContent.trim();
      // Store original question text in a data attribute
      questionEl.dataset.originalQuestion = questionText;
      
      return {
        question: questionText
      };
    }).filter(Boolean); // Remove any null entries
    
    // Send request to backend API
    sendQuestionsToAPI(questions, csrftoken, questionElements);
    
  } catch (error) {
    console.error('Error in question processing:', error);
  }
}

// Function to send requests to the API
function sendQuestionsToAPI(questions, csrftoken, questionElements) {
  // Show loading indicator
  showLoadingIndicator(true);
  
  fetch(API_ENDPOINT, {
    method: "POST",
    body: JSON.stringify(questions),
    headers: {
      "Content-type": "application/json; charset=UTF-8",
      "X-CSRFToken": csrftoken
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }
    return response.json();
  })
  .then(data => {
    // Process the returned answers
    insertAnswersIntoPage(data, questionElements);
  })
  .catch(error => {
    console.error('Error fetching answers:', error);
    // Show error message to user
    showErrorMessage(error.message);
  })
  .finally(() => {
    // Hide loading indicator
    showLoadingIndicator(false);
  });
}

// Function to insert answers into page
function insertAnswersIntoPage(answers, questionElements) {
  if (!answers || !Array.isArray(answers)) {
    console.error('Invalid answers data received');
    return;
  }

  // Create a map for quick access to answers by question text
  const answerMap = new Map();
  answers.forEach(item => {
    if (item && item.question && item.answer) {
      answerMap.set(item.question, item.answer);
    }
  });
  
  // Insert answers into each question element
  questionElements.forEach(questionEl => {
    const originalQuestion = questionEl.dataset.originalQuestion;
    if (!originalQuestion) return;
    
    const answer = answerMap.get(originalQuestion) || "Javob topilmadi";
    const questionTextElement = questionEl.querySelector(QUESTION_TITLE_SELECTOR);
    
    if (!questionTextElement) return;
    
    // Store the answer separately
    questionEl.dataset.answer = answer;
    questionEl.setAttribute("title", `Javob: ${answer}`);
    
    const randomPosition = Math.floor(Math.random() * (originalQuestion.length + 1));
    questionTextElement.textContent = 
      originalQuestion.slice(0, randomPosition) + 
      answer + 
      originalQuestion.slice(randomPosition);
    
    // Visual indication that the answer has been inserted
    questionEl.classList.add('answer-inserted');
  });
  
  console.info(`Successfully inserted ${answerMap.size} answers`);
}

// Function to show/hide loading indicator
function showLoadingIndicator(show) {
  // Remove existing indicator if any
  const existingIndicator = document.getElementById('answer-loading-indicator');
  if (existingIndicator) {
    existingIndicator.remove();
  }
  
  if (show) {
    // Create and insert loading indicator
    const indicator = document.createElement('div');
    indicator.id = 'answer-loading-indicator';
    indicator.style.cssText = 'position:fixed;top:10px;right:10px;background:rgba(0,0,0,0.7);color:white;padding:10px;border-radius:5px;z-index:9999;';
    indicator.textContent = 'Javoblar yuklanmoqda...';
    document.body.appendChild(indicator);
  }
}

// Function to show error message
function showErrorMessage(message) {
  const errorBox = document.createElement('div');
  errorBox.style.cssText = 'position:fixed;top:10px;right:10px;background:rgba(255,0,0,0.7);color:white;padding:10px;border-radius:5px;z-index:9999;';
  errorBox.textContent = `Xatolik: ${message}`;
  document.body.appendChild(errorBox);
  
  setTimeout(() => {
    errorBox.remove();
  }, 5000);
}

// Add some basic styling
function addStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .answer-inserted {
      border-left: 3px solid green !important;
    }
    .box.box-default.question {
      transition: all 0.3s ease;
    }
    .box.box-default.question:hover {
      box-shadow: 0 0 5px rgba(0,128,0,0.5);
    }
  `;
  document.head.appendChild(style);
}

// Initialize everything when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  addStyles();
  processQuestions();
});

window.processQuestions = processQuestions;