import sys
import os
import sqlite3
from flask import Flask, render_template, request

# Add parent dir to sys.path to resolve imports properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import get_db_connection, init_db
from database.models import get_all_jobs
from recommendation.ranking import get_ranked_jobs

app = Flask(__name__)

# Initialize DB
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        skills = request.form.get('skills', '')
        experience = request.form.get('experience', '')
        location = request.form.get('location', '')
        
        # Combine user traits into a single profile document for NLP matching
        user_profile = f"{skills} {experience} {location}"
        
        # Save user to DB (optional step as per prompt requirements)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO Users (name, skills, experience, location) 
            VALUES (?, ?, ?, ?)
        ''', ('Anonymous', skills, experience, location))
        conn.commit()
        conn.close()
        
        # Fetch all jobs
        jobs_list = get_all_jobs()
        
        # Rank jobs
        ranked_jobs = get_ranked_jobs(user_profile, jobs_list, top_n=10)
        
        # Split skills for highlighting
        skill_list = [s.strip().lower() for s in skills.split(',')] if skills else []
        
        return render_template('results.html', jobs=ranked_jobs, skills=skill_list)
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
