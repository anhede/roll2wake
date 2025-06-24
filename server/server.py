from flask import Flask, request, jsonify
import os
from storyteller import Storyteller
from stats import Statistics
from datetime import datetime

app = Flask(__name__)

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable is not set")
storyteller = Storyteller(api_key=api_key, model="gpt-4.1-mini")

@app.route('/new', methods=['GET'])
def get_new_story():
    """GET endpoint to start a new story"""
    try:
        story_beat = storyteller.generate_new_story()
        print(f"New story beat generated: {story_beat.to_dict()}")
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
        print(f"Received update request with choice_id: {choice_id}, success_result: {success_result}")
        
        if choice_id is None or success_result is None:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: choice_id and success_result'
            }), 400
        
        story_beat = storyteller.continue_story(choice_id=choice_id, success_result=success_result)
        print(f"Story beat updated: {story_beat.to_dict()}")
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

def handle_statistic(stat: Statistics):
    # Insert your business logic here. For example:
    print(f"Got {stat.type} = {stat.value} at {stat.timestamp!r}")

@app.route('/stats', methods=['POST'])
def post_stats():
    payload = request.get_json(force=True)
    try:
        stat = Statistics.from_dict(payload)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # if you need a datetime object, do it here:
    ts = stat.timestamp
    if isinstance(ts, str):
        try:
            stat.timestamp = datetime.fromisoformat(ts)  # CPython 3.7+
        except Exception:
            pass  # leave it as string if parsing fails

    handle_statistic(stat)
    return jsonify({'status': 'ok'}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
