"""
PredictX AI Portal — Flask Backend
Run: python app.py
"""
from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'predictx-dev-secret-2024')

    # Allow React dev server on port 3000
    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]}}, supports_credentials=True)

    # Register all route blueprints
    from routes.auth     import auth_bp
    from routes.gold     import gold_bp
    from routes.fraud    import fraud_bp
    from routes.spam     import spam_bp
    from routes.rainfall import rainfall_bp

    app.register_blueprint(auth_bp,     url_prefix='/api/auth')
    app.register_blueprint(gold_bp,     url_prefix='/api/gold')
    app.register_blueprint(fraud_bp,    url_prefix='/api/fraud')
    app.register_blueprint(spam_bp,     url_prefix='/api/spam')
    app.register_blueprint(rainfall_bp, url_prefix='/api/rainfall')

    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'PredictX is running ✅'}

    return app

if __name__ == '__main__':
    app = create_app()

    port = int(os.environ.get("PORT", 5000))

    print("\n🧠 PredictX AI Portal — Backend")
    print(f"   Running at: http://0.0.0.0:{port}")
    print(f"   API Health: http://0.0.0.0:{port}/api/health\n")

    app.run(host="0.0.0.0", port=port)
