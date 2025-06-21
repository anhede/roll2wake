from flask import Flask, request, jsonify
import os
from storyteller import Storyteller
from models import StoryBeat

app = Flask(__name__)

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable is not set")
storyteller = Storyteller(api_key=api_key)

@app.route('/new', methods=['GET'])
def get_new_story():
    """GET endpoint to start a new story"""
    try:
        story_beat = storyteller.generate_new_story()
        
        return jsonify({
            'success': True,
            'story_beat': story_beat.to_dict()
        })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/update', methods=['POST'])
def update_story():
    """POST endpoint to continue the story with a choice and result"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        choice_id = data.get('choice_id')
        success_result = data.get('success_result')
        
        if choice_id is None or success_result is None:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: choice_id and success_result'
            }), 400
        
        story_beat = storyteller.continue_story(choice_id=choice_id, success_result=success_result)
        
        return jsonify({
            'success': True,
            'story_beat': story_beat.to_dict()
        })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'storyteller-api'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
