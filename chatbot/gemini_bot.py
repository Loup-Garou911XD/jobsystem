import sys
import os
import json
import re
from typing import Dict, List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Add parent dir to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import GEMINI_API_KEY
from database.models import get_all_jobs
from recommendation.ranking import get_ranked_jobs


class JobChatBot:
    """Gemini-based chatbot for job recommendations."""

    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        '''Initialize the chatbot with Gemini model.'''
        self.model = ChatGoogleGenerativeAI(model=model_name, google_api_key=GEMINI_API_KEY)
        self.conversation_history = []
        self.user_profile = {'skills': [], 'experience': '', 'location': ''}
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        '''Build the system prompt for the chatbot.'''
        return """You are a friendly and helpful Job Recommendation Assistant powered by AI.
Your role is to:
1. Have a natural conversation with the user
2. Extract their professional skills, years of experience, and desired location
3. Understand their career goals and preferences
4. Provide relevant job recommendations based on their profile

Guidelines:
- Be conversational and friendly
- Ask clarifying questions if needed
- Extract skills as a comma-separated list
- Remember information from previous messages
- When you have enough information (skills, experience level, and location), let the user know you can find jobs for them
- Format any job recommendations clearly with job title, company, and key details

If the user provides job recommendations context, format them nicely.
For extracted information, mark it clearly so the system can parse it.

When you have gathered skills, experience, and location, include this at the end of a message:
[PROFILE_READY: skills=SKILL1,SKILL2,SKILL3 experience=LEVEL location=LOCATION]

This helps the system know when to fetch actual job recommendations."""

    def chat(self, user_message: str) -> str:
        '''Send a message and get a response from the chatbot.'''
        # Prepare messages for LangChain
        messages = [SystemMessage(content=self.system_prompt)]

        # Add conversation history
        for msg in self.conversation_history:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))

        # Add current user message
        messages.append(HumanMessage(content=user_message))

        # Get response from LangChain/Gemini
        response = self.model.invoke(messages)

        # Extract text from response - handle various formats
        bot_response = self._extract_text_from_response(response)

        # Add to conversation history
        self.conversation_history.append({'role': 'user', 'content': user_message})
        self.conversation_history.append({'role': 'assistant', 'content': bot_response})

        # Extract profile information from response
        self._extract_profile_info(bot_response)

        return bot_response

    def _extract_text_from_response(self, response) -> str:
        '''Extract text from various response formats.'''
        # If response is a dict or has dict-like attributes
        if isinstance(response, dict):
            # Handle {'type': 'text', 'text': '...'}
            if 'text' in response:
                return str(response['text'])
            elif 'content' in response:
                return str(response['content'])

        # Check if response has a 'content' attribute
        if hasattr(response, 'content'):
            content = response.content
            # If content is a dict with 'text' key
            if isinstance(content, dict):
                if 'text' in content:
                    return str(content['text'])
                elif 'type' in content and content.get('type') == 'text':
                    return str(content.get('text', ''))
            # If content is a list (e.g., multiple content blocks)
            elif isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(str(item['text']))
                    elif isinstance(item, str):
                        text_parts.append(str(item))
                if text_parts:
                    return ''.join(text_parts)
            # If content is already a string
            else:
                return str(content)

        # Fallback: convert to string
        return str(response)

    def _extract_profile_info(self, response: str) -> None:
        '''Extract skills, experience, and location from conversation.'''
        # Ensure response is a string
        if not isinstance(response, str):
            response = str(response)

        # Look for profile markers in the response
        profile_match = re.search(
            r'\[PROFILE_READY:\s*skills=([^&]+?)\s+experience=([^&]+?)\s+location=([^\]]+)\]',
            response,
        )

        if profile_match:
            skills_str = profile_match.group(1).strip()
            exp_str = profile_match.group(2).strip()
            loc_str = profile_match.group(3).strip()

            # Parse skills
            self.user_profile['skills'] = [s.strip() for s in skills_str.split(',')]
            self.user_profile['experience'] = exp_str
            self.user_profile['location'] = loc_str

    def get_recommendations(self, top_n: int = 10) -> List[Dict]:
        '''Get job recommendations based on collected profile.'''
        if not self.user_profile['skills']:
            return []

        # Create user profile string for ranking
        user_profile_str = f"{' '.join(self.user_profile['skills'])} {self.user_profile['experience']} {self.user_profile['location']}"

        # Fetch all jobs
        jobs_list = get_all_jobs()

        if not jobs_list:
            return []

        # Rank jobs
        ranked_jobs = get_ranked_jobs(user_profile_str, jobs_list, top_n=top_n)

        return ranked_jobs

    def get_profile(self) -> Dict:
        '''Get the current user profile.'''
        return self.user_profile

    def reset(self) -> None:
        '''Reset the conversation and profile.'''
        self.conversation_history = []
        self.user_profile = {'skills': [], 'experience': '', 'location': ''}
