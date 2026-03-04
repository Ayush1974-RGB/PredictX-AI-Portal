"""
PredictX AI Portal — Flask Backend
Run locally: python app.py
"""
from flask import Flask
from flask_cors import CORS
import os, joblib

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")

model = joblib.load(MODEL_PATH)

def create_app():
    app = Flask(__name__)

    # Secret key
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "predictx-dev-secret-2024")

    # CORS configuration
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},  # allow all for now
        supports_credentials=True
    )

    # Import route blueprints
    from routes.auth import auth_bp
    from routes.gold import gold_bp
    from routes.fraud import fraud_bp
    from routes.spam import spam_bp
    from routes.rainfall import rainfall_bp

    # Register routes
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(gold_bp, url_prefix="/api/gold")
    app.register_blueprint(fraud_bp, url_prefix="/api/fraud")
    app.register_blueprint(spam_bp, url_prefix="/api/spam")
    app.register_blueprint(rainfall_bp, url_prefix="/api/rainfall")

    # Health check endpoint
    @app.route("/api/health")
    def health():
        return {
            "status": "ok",
            "message": "PredictX AI Portal backend running 🚀"
        }

    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print("\n🧠 PredictX AI Portal — Backend")
    print(f"Running on port: {port}")

    app.run(host="0.0.0.0", port=port)