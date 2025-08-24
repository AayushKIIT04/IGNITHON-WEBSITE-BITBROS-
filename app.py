from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

# Initialize Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database & upload setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------- Models ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    problem_type = db.Column(db.String(50), nullable=False)
    locality = db.Column(db.String(100), nullable=False)
    problem = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(200))
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))

class QuizScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)

# Create DB tables
with app.app_context():
    db.create_all()

# ---------------- Routes ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        email = request.form.get('email', '').strip()
        
        if not name or not gender or not email:
            flash("Please fill all fields!", "error")
            return redirect(url_for("index"))
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return redirect(url_for('dashboard', user_id=existing_user.id))
        
        user = User(name=name, gender=gender, email=email)
        db.session.add(user)
        db.session.commit()
        flash(f"Welcome {name}! Let's make a difference together.", "success")
        return redirect(url_for('dashboard', user_id=user.id))
    
    return render_template("index.html")

@app.route("/dashboard/<int:user_id>")
def dashboard(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("dashboard.html", user_id=user_id, user=user)

@app.route("/report/<int:user_id>", methods=["GET", "POST"])
def report(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        problem_type = request.form.get('problem_type', '').strip()
        locality = request.form.get('locality', '').strip()
        problem = request.form.get('problem', '').strip()
        latitude = request.form.get('latitude', '').strip()
        longitude = request.form.get('longitude', '').strip()
        
        if not all([problem_type, locality, problem]):
            flash("Please fill all required fields!", "error")
            return redirect(url_for('report', user_id=user_id))
        
        # Image upload (optional)
        image_path = None
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
        
        new_report = Report(
            user_id=user_id,
            problem_type=problem_type,
            locality=locality,
            problem=problem,
            image=image_path,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(new_report)
        db.session.commit()
        
        flash(f"Report submitted successfully! Thank you for helping conserve water.", "success")
        return redirect(url_for('dashboard', user_id=user_id))
    
    return render_template("report.html", user_id=user_id, user=user)

@app.route("/tips/<int:user_id>")
def tips(user_id):
    user = User.query.get_or_404(user_id)
    
    tips_categories = {
        "Water Conservation": [
            "Turn off taps while brushing teeth - save up to 8 gallons per day",
            "Fix leaky faucets immediately - a single drip can waste 3,000 gallons per year",
            "Use a bucket instead of a hose for washing cars",
            "Install water-efficient showerheads and toilets",
            "Collect rainwater for gardening and non-potable uses",
            "Use greywater from washing machines for irrigation"
        ],
        "Hygiene & Sanitation": [
            "Wash hands with soap for at least 20 seconds",
            "Use clean, safe drinking water sources",
            "Maintain proper toilet hygiene and sanitation",
            "Keep water storage containers clean and covered",
            "Practice safe food handling with clean water",
            "Ensure proper waste disposal to prevent water contamination"
        ],
        "Community Action": [
            "Report water leaks in public areas immediately",
            "Educate family and friends about water conservation",
            "Participate in local water conservation programs",
            "Support policies for clean water access",
            "Monitor your water usage with smart meters",
            "Join community clean-up drives for water bodies"
        ]
    }
    
    return render_template("tips.html", tips_categories=tips_categories, user_id=user_id, user=user)

@app.route("/quiz/<int:user_id>", methods=["GET", "POST"])
def quiz(user_id):
    user = User.query.get_or_404(user_id)
    
    questions = [
        {
            "q": "How much water should an average adult drink daily according to WHO?",
            "options": ["1-2 liters", "2-3 liters", "3-4 liters", "5+ liters"],
            "answer": "2-3 liters",
            "explanation": "WHO recommends 2-3 liters of water daily for proper hydration and health."
        },
        {
            "q": "What percentage of Earth's water is freshwater suitable for human use?",
            "options": ["10%", "5%", "3%", "Less than 1%"],
            "answer": "Less than 1%",
            "explanation": "Only 0.3% of Earth's water is accessible freshwater, making conservation crucial."
        },
        {
            "q": "Which is the most effective way to prevent waterborne diseases?",
            "options": ["Boiling water", "Using soap", "Proper sanitation", "All of the above"],
            "answer": "All of the above",
            "explanation": "Combining safe water, hygiene, and sanitation prevents most waterborne diseases."
        },
        {
            "q": "How long should you wash your hands to remove germs effectively?",
            "options": ["5 seconds", "10 seconds", "20 seconds", "1 minute"],
            "answer": "20 seconds",
            "explanation": "20 seconds of handwashing with soap removes 99.9% of germs effectively."
        },
        {
            "q": "What is the UN Sustainable Development Goal 6 about?",
            "options": ["Clean energy", "Clean water and sanitation", "Climate action", "Zero hunger"],
            "answer": "Clean water and sanitation",
            "explanation": "SDG 6 aims to ensure clean water and sanitation for all by 2030."
        }
    ]
    
    if request.method == "POST":
        score = 0
        results = []
        
        for i, question in enumerate(questions):
            selected = request.form.get(f"q{i}")
            is_correct = selected == question["answer"]
            if is_correct:
                score += 1
            
            results.append({
                "question": question["q"],
                "selected": selected,
                "correct": question["answer"],
                "is_correct": is_correct,
                "explanation": question["explanation"]
            })
        
        new_score = QuizScore(user_id=user_id, score=score)
        db.session.add(new_score)
        db.session.commit()
        
        return render_template("quiz_results.html", 
                             score=score, 
                             total=len(questions), 
                             results=results, 
                             user_id=user_id, 
                             user=user)
    
    return render_template("quiz.html", questions=questions, user_id=user_id, user=user)

@app.route("/stats/<int:user_id>")
def stats(user_id):
    user = User.query.get_or_404(user_id)
    reports = Report.query.filter_by(user_id=user_id).all()
    quiz_scores = QuizScore.query.filter_by(user_id=user_id).all()
    
    # Analytics data
    locality_count = {}
    problem_type_count = {"Public": 0, "Private": 0}
    
    for r in reports:
        if r.locality:
            locality_count[r.locality] = locality_count.get(r.locality, 0) + 1
        problem_type_count[r.problem_type] += 1
    
    scores = [q.score for q in quiz_scores]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return render_template("stats.html", 
                         reports=reports,
                         locality_count=locality_count,
                         problem_type_count=problem_type_count,
                         scores=scores,
                         avg_score=round(avg_score, 1),
                         user_id=user_id,
                         user=user)

if __name__ == "__main__":
    app.run(debug=True)
