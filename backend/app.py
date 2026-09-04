import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from routes.analyze import analyze_bp
from routes.health import health_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(analyze_bp, url_prefix='/api')
    
    # Global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"error": str(e)}), 500
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
