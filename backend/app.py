from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import os
import json
import logging

from ai_screen_reader import AIScreenReader, ActionCommand

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
CORS(app)

screen_reader = None

@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/initialize', methods=['POST'])
def initialize_screen_reader():
    """Initialize the AI Screen Reader with API key"""
    global screen_reader
    
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        
        if not api_key:
            return jsonify({"error": "API key is required"}), 400
        
        screen_reader = AIScreenReader(api_key)
        
        return jsonify({
            "status": "initialized",
            "message": "AI Screen Reader initialized successfully"
        })
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze/detailed', methods=['POST'])
def analyze_screen_detailed():
    """Analyze current screen and return detailed explanations"""
    global screen_reader
    
    if not screen_reader:
        return jsonify({"error": "Screen reader not initialized"}), 400
    
    try:

        result = screen_reader.analyze_current_screen()
        
        if "error" in result:
            return jsonify(result), 500
        
        result['analysis_id'] = f"analysis_{int(datetime.utcnow().timestamp())}"
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Detailed screen analysis failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/explain', methods=['POST'])
def explain_screen():
    """Get detailed explanation of what's on the current screen"""
    global screen_reader
    
    if not screen_reader:
        return jsonify({"error": "Screen reader not initialized"}), 400
    
    try:
        data = request.get_json()
        user_intent = data.get('user_intent', '')
        
        screenshot = screen_reader.screen_capture.capture_screen()
        if screenshot is None:
            return jsonify({"error": "Failed to capture screen"}), 500
        
        import cv2
        import base64
        _, buffer = cv2.imencode('.jpg', screenshot)
        screenshot_b64 = base64.b64encode(buffer).decode('utf-8')
        
        explanation = screen_reader.llm_interface.interpret_screen_context(screenshot_b64, user_intent)
        
        return jsonify({
            "timestamp": datetime.utcnow().isoformat(),
            "explanation": explanation,
            "screenshot_b64": screenshot_b64
        })
        
    except Exception as e:
        logger.error(f"Screen explanation failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """Start continuous screen monitoring"""
    global screen_reader
    
    if not screen_reader:
        return jsonify({"error": "Screen reader not initialized"}), 400
    
    try:
        data = request.get_json()
        interval = data.get('interval', 2.0)
        
        screen_reader.start_monitoring(interval)
        
        return jsonify({
            "status": "monitoring_started",
            "interval": interval,
            "message": "Screen monitoring started successfully"
        })
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitoring():
    """Stop screen monitoring"""
    global screen_reader
    
    if not screen_reader:
        return jsonify({"error": "Screen reader not initialized"}), 400
    
    try:
        screen_reader.stop_monitoring()
        
        return jsonify({
            "status": "monitoring_stopped",
            "message": "Screen monitoring stopped successfully"
        })
        
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:

        stats = {
            "total_analyses": 0,
            "total_commands": 0,
            "executed_commands": 0,
            "recent_analyses": 0,
            "success_rate": 0
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
