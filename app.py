from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "https://teacher-suggestion-app.netlify.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load environment variables
load_dotenv()

LLAMA_API_KEY = "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"

@app.route('/api/get-teaching-suggestion', methods=['POST', 'OPTIONS'])
def get_teaching_suggestion():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        required_fields = ['numStudents', 'level', 'learningStyle', 'subject']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        num_students = data['numStudents']
        level = data['level']
        learning_style = data['learningStyle']
        subject = data['subject']
        custom_query = data.get('customQuery', '')

        # Construct the prompt for Llama
        prompt = f"""As an expert educational consultant, provide teaching suggestions for the following scenario:
        Number of Students: {num_students}
        Student Level: {level}
        Learning Style: {learning_style}
        Subject: {subject}
        Additional Requirements: {custom_query}

        Please provide specific teaching strategies, activities, and methods that would be most effective for this group,
        focusing on interactive and engaging approaches."""

        print(f"Making API request with prompt: {prompt}")

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {LLAMA_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Teacher Suggestion API",
            },
            json={
                "model": "meta-llama/llama-4-maverick:free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        )
        
        print(f"API Response status code: {response.status_code}")
        
        if response.status_code == 200:
            suggestion = response.json()
            print(f"API Response: {suggestion}")
            return jsonify({"success": True, "suggestion": suggestion})
        else:
            error_message = f"API Error: {response.text}"
            print(error_message)
            return jsonify({"success": False, "error": error_message}), response.status_code

    except requests.exceptions.RequestException as e:
        error_message = f"Network error: {str(e)}"
        print(error_message)
        return jsonify({"success": False, "error": error_message}), 503
    except Exception as e:
        error_message = f"Server error: {str(e)}"
        print(error_message)
        return jsonify({"success": False, "error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
