from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'message': '🤖 AgriSmart ML Service is running!',
        'status': 'success',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'ML Service'})

if __name__ == '__main__':
    port = int(os.getenv('ML_PORT', 5001))  # Changed to 5001
    app.run(host='0.0.0.0', port=port, debug=True)
