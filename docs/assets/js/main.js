/**
 * The Second Self - Main JavaScript
 * 12주 영어 학습 커리큘럼 웹사이트
 */

// ============================================
// Mobile Navigation Toggle
// ============================================
function initMobileNav() {
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      const isOpen = navLinks.classList.contains('active');
      navToggle.setAttribute('aria-expanded', isOpen);
      navToggle.innerHTML = isOpen ? '✕' : '☰';
    });
  }
}

// ============================================
// Audio Player with Speed Control
// ============================================
function initAudioPlayer() {
  const audioPlayers = document.querySelectorAll('.audio-player');
  
  audioPlayers.forEach(player => {
    const audio = player.querySelector('audio');
    const speedButtons = player.querySelectorAll('.speed-btn');
    
    if (!audio) return;
    
    speedButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const speed = parseFloat(btn.dataset.speed);
        audio.playbackRate = speed;
        
        // Update active state
        speedButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  });
}

// ============================================
// Vocabulary Flashcards
// ============================================
function initFlashcards() {
  const vocabCards = document.querySelectorAll('.vocab-card');
  
  vocabCards.forEach(card => {
    card.addEventListener('click', () => {
      card.classList.toggle('flipped');
    });
  });
}

// ============================================
// Quiz Functionality
// ============================================
function initQuiz() {
  const quizSections = document.querySelectorAll('.quiz-section');
  
  quizSections.forEach(section => {
    const options = section.querySelectorAll('.quiz-option');
    const correctAnswer = section.dataset.answer;
    
    options.forEach(option => {
      option.addEventListener('click', () => {
        // Prevent re-selection
        if (section.classList.contains('answered')) return;
        
        section.classList.add('answered');
        const selectedValue = option.dataset.value;
        
        if (selectedValue === correctAnswer) {
          option.classList.add('correct');
        } else {
          option.classList.add('incorrect');
          // Show correct answer
          options.forEach(opt => {
            if (opt.dataset.value === correctAnswer) {
              opt.classList.add('correct');
            }
          });
        }
      });
    });
  });
}

// ============================================
// Fill in the Blanks
// ============================================
function initFillBlanks() {
  const fillBlanks = document.querySelectorAll('.fill-blank');
  
  fillBlanks.forEach(blank => {
    const input = blank.querySelector('input');
    const correctAnswer = blank.dataset.answer?.toLowerCase();
    
    if (!input || !correctAnswer) return;
    
    input.addEventListener('blur', () => {
      const userAnswer = input.value.trim().toLowerCase();
      
      if (userAnswer === correctAnswer) {
        blank.classList.add('correct');
        blank.classList.remove('incorrect');
      } else if (userAnswer !== '') {
        blank.classList.add('incorrect');
        blank.classList.remove('correct');
      }
    });
  });
}

// ============================================
// Reveal Answers
// ============================================
function initRevealAnswers() {
  const revealButtons = document.querySelectorAll('.reveal-answer-btn');
  
  revealButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      const answerEl = document.getElementById(targetId);
      
      if (answerEl) {
        answerEl.classList.toggle('hidden');
        btn.textContent = answerEl.classList.contains('hidden') 
          ? '정답 보기' 
          : '정답 숨기기';
      }
    });
  });
}

// ============================================
// Smooth Scroll for Anchor Links
// ============================================
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

// ============================================
// Reading Progress (for long pages)
// ============================================
function initReadingProgress() {
  const progressBar = document.querySelector('.reading-progress');
  if (!progressBar) return;
  
  window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (scrollTop / docHeight) * 100;
    progressBar.style.width = `${progress}%`;
  });
}

// ============================================
// Initialize All Functions
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initAudioPlayer();
  initFlashcards();
  initQuiz();
  initFillBlanks();
  initRevealAnswers();
  initSmoothScroll();
  initReadingProgress();
  
  console.log('The Second Self - Ready! 🚀');
});
