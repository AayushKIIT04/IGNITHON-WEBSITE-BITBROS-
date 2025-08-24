// DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  // Auto-hide flash messages after 5 seconds
  const flashMessages = document.querySelectorAll(".flash-message")
  flashMessages.forEach((message) => {
    setTimeout(() => {
      message.style.transition = "opacity 0.5s ease, transform 0.5s ease"
      message.style.opacity = "0"
      message.style.transform = "translateX(-20px)"
      setTimeout(() => message.remove(), 500)
    }, 5000)
  })

  // Button ripple effect
  document.querySelectorAll(".btn").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      const rect = this.getBoundingClientRect()
      const ripple = document.createElement("span")
      ripple.classList.add("ripple")
      ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple-effect 0.6s linear;
                left: ${e.clientX - rect.left - 25}px;
                top: ${e.clientY - rect.top - 25}px;
                width: 50px;
                height: 50px;
                pointer-events: none;
            `
      this.appendChild(ripple)
      setTimeout(() => ripple.remove(), 600)
    })
  })

  // Geolocation for report form
  const latInput = document.getElementById("latitude")
  const lonInput = document.getElementById("longitude")

  if (latInput && lonInput && navigator.geolocation) {
    // Show loading state
    latInput.placeholder = "Getting location..."
    lonInput.placeholder = "Getting location..."

    navigator.geolocation.getCurrentPosition(
      (position) => {
        latInput.value = position.coords.latitude.toFixed(6)
        lonInput.value = position.coords.longitude.toFixed(6)
        latInput.placeholder = "Latitude detected"
        lonInput.placeholder = "Longitude detected"

        // Add success styling
        latInput.style.borderColor = "#10b981"
        lonInput.style.borderColor = "#10b981"
      },
      (error) => {
        console.log("Geolocation error:", error.message)
        latInput.placeholder = "Location unavailable"
        lonInput.placeholder = "Location unavailable"

        // Add warning styling
        latInput.style.borderColor = "#f59e0b"
        lonInput.style.borderColor = "#f59e0b"
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000, // 5 minutes
      },
    )
  }

  // Form validation enhancement
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      const requiredFields = form.querySelectorAll("[required]")
      let isValid = true

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          field.style.borderColor = "#ef4444"
          field.style.boxShadow = "0 0 0 3px rgba(239, 68, 68, 0.1)"
          isValid = false
        } else {
          field.style.borderColor = "#10b981"
          field.style.boxShadow = "0 0 0 3px rgba(16, 185, 129, 0.1)"
        }
      })

      if (!isValid) {
        e.preventDefault()
        // Show error message
        showNotification("Please fill in all required fields", "error")
      }
    })
  })

  // Quiz progress tracking
  const quizForm = document.querySelector(".quiz-form")
  if (quizForm) {
    const questions = quizForm.querySelectorAll(".question-card")
    const progressBar = createProgressBar(questions.length)
    quizForm.insertBefore(progressBar, quizForm.firstChild)

    questions.forEach((question, index) => {
      const radioButtons = question.querySelectorAll('input[type="radio"]')
      radioButtons.forEach((radio) => {
        radio.addEventListener("change", () => {
          updateProgress(progressBar, questions)
        })
      })
    })
  }

  // Smooth scrolling for navigation
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })

  // Dashboard card hover effects
  const dashboardCards = document.querySelectorAll(".dashboard-card")
  dashboardCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-8px) scale(1.02)"
    })

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0) scale(1)"
    })
  })
})

// Utility Functions
function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `flash-message flash-${type}`
  notification.innerHTML = `
        <i class="fas fa-${type === "success" ? "check-circle" : "exclamation-triangle"}"></i>
        ${message}
    `

  document.body.appendChild(notification)

  // Position notification
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `

  setTimeout(() => {
    notification.style.opacity = "0"
    notification.style.transform = "translateX(100%)"
    setTimeout(() => notification.remove(), 300)
  }, 4000)
}

function createProgressBar(totalQuestions) {
  const progressContainer = document.createElement("div")
  progressContainer.className = "quiz-progress"
  progressContainer.innerHTML = `
        <div class="progress-bar">
            <div class="progress-fill" style="width: 0%"></div>
        </div>
        <span class="progress-text">0 of ${totalQuestions} questions answered</span>
    `

  // Add CSS for progress bar
  const style = document.createElement("style")
  style.textContent = `
        .quiz-progress {
            margin-bottom: 2rem;
            text-align: center;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #0ea5e9, #10b981);
            transition: width 0.3s ease;
        }
        .progress-text {
            font-size: 0.9rem;
            color: #64748b;
        }
    `
  document.head.appendChild(style)

  return progressContainer
}

function updateProgress(progressBar, questions) {
  const answeredQuestions = Array.from(questions).filter((question) => {
    const radios = question.querySelectorAll('input[type="radio"]')
    return Array.from(radios).some((radio) => radio.checked)
  })

  const progress = (answeredQuestions.length / questions.length) * 100
  const progressFill = progressBar.querySelector(".progress-fill")
  const progressText = progressBar.querySelector(".progress-text")

  progressFill.style.width = `${progress}%`
  progressText.textContent = `${answeredQuestions.length} of ${questions.length} questions answered`
}

// Add CSS animations
const style = document.createElement("style")
style.textContent = `
    @keyframes ripple-effect {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`
document.head.appendChild(style)
