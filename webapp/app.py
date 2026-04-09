import sys
import os
import sqlite3
import json
from flask import Flask, render_template, request, jsonify, session

# Add parent dir to sys.path to resolve imports properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import get_db_connection, init_db
from database.models import get_all_jobs
from recommendation.ranking import get_ranked_jobs
from chatbot.gemini_bot import JobChatBot

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Initialize DB
init_db()

# Store chatbot instances per session
chatbots = {}


def get_or_create_chatbot(session_id: str) -> JobChatBot:
    '''Get or create a chatbot instance for the session.'''
    if session_id not in chatbots:
        chatbots[session_id] = JobChatBot()
    return chatbots[session_id]


@app.route('/', methods=['GET'])
def index():
    '''Render the chat interface.'''
    return render_template('chat.html')


@app.route('/classic', methods=['GET', 'POST'])
def classic():
    '''Original form-based interface for job recommendations.'''
    if request.method == 'POST':
        skills = request.form.get('skills', '')
        experience = request.form.get('experience', '')
        location = request.form.get('location', '')

        # Combine user traits into a single profile document for NLP matching
        user_profile = f"{skills} {experience} {location}"

        # Save user to DB (optional step as per prompt requirements)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            '''
            INSERT INTO Users (name, skills, experience, location) 
            VALUES (?, ?, ?, ?)
        ''',
            ('Anonymous', skills, experience, location),
        )
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


@app.route('/api/chat', methods=['POST'])
def chat():
    '''Handle chat messages from the user.'''
    try:
        data = request.json
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Get or create session ID
        if 'chatbot_session' not in session:
            session['chatbot_session'] = os.urandom(16).hex()

        session_id = session['chatbot_session']
        chatbot = get_or_create_chatbot(session_id)

        # Get response from chatbot
        bot_response = chatbot.chat(user_message)

        # Get current profile
        profile = chatbot.get_profile()

        # Check if we have enough info to fetch jobs
        recommendations = []
        if profile['skills'] and profile['experience'] and profile['location']:
            recommendations = chatbot.get_recommendations(top_n=10)

        return jsonify(
            {
                'response': bot_response,
                'profile': profile,
                'recommendations': (
                    [
                        {
                            'id': job.get('id'),
                            'title': job.get('title'),
                            'company': job.get('company'),
                            'location': job.get('location'),
                            'url': job.get('url'),
                            'description': job.get('description', '')[:200],
                        }
                        for job in recommendations
                    ]
                    if recommendations
                    else []
                ),
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-jobs', methods=['POST'])
def get_jobs():
    '''Get job recommendations based on current profile.'''
    try:
        if 'chatbot_session' not in session:
            return jsonify({'error': 'No active chat session'}), 400

        session_id = session['chatbot_session']
        chatbot = get_or_create_chatbot(session_id)
        profile = chatbot.get_profile()

        if not profile['skills'] or not profile['experience'] or not profile['location']:
            return jsonify({'error': 'Incomplete profile'}), 400

        recommendations = chatbot.get_recommendations(top_n=10)

        return jsonify(
            {
                'jobs': [
                    {
                        'id': job.get('id'),
                        'title': job.get('title'),
                        'company': job.get('company'),
                        'location': job.get('location'),
                        'url': job.get('url'),
                        'description': job.get('description', ''),
                    }
                    for job in recommendations
                ]
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_chat():
    '''Reset the chat session.'''
    try:
        if 'chatbot_session' in session:
            session_id = session['chatbot_session']
            if session_id in chatbots:
                del chatbots[session_id]
            del session['chatbot_session']

        return jsonify({'status': 'reset'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
