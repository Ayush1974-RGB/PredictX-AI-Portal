from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "predictx-dev-secret")

    # Allow all origins — safe for a portfolio project
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import routes
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

    @app.route("/")
    def home():
        return {"message": "PredictX Backend Running 🚀"}

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)