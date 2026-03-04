"""
routes/spam.py — Spam Email Detection
"""
from flask import Blueprint, request, jsonify
import joblib, os

spam_bp   = Blueprint('spam', __name__)
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

@spam_bp.route('/predict', methods=['POST'])
def predict():
    try:
        d    = request.get_json()
        subj = d.get('subject', '')
        body = d.get('body', '')
        text = f"{subj} {body}".strip()

        if not text:
            return jsonify({'error': 'Email content required'}), 400

        try:
            model     = joblib.load(os.path.join(MODEL_DIR, 'spam_model.pkl'))
            pred      = model.predict([text])[0]
            proba     = model.predict_proba([text])[0]
            is_spam   = bool(pred == 1)
            spam_prob = float(proba[1]) * 100
            confidence= float(max(proba)) * 100

        except Exception:
            # Fallback: TF-IDF weighted keyword scoring
            import math
            words = text.lower().split()
            spam_tokens = {
                'free':2.4,'win':2.1,'winner':2.8,'won':2.3,'prize':2.9,
                'cash':2.1,'claim':2.6,'urgent':2.0,'congratulations':2.7,
                'offer':1.6,'limited':1.5,'click':1.9,'guaranteed':2.5,
                'selected':1.8,'billion':2.2,'million':2.0,'bank':1.4,
                'password':1.7,'verify':1.5,'immediately':1.8,'lottery':3.1,
                'nigeria':3.2,'inheritance':2.9,'crypto':1.2,'earn':1.7,
            }
            ham_tokens = {
                'meeting':-1.8,'team':-1.5,'project':-1.6,'please':-0.9,
                'thanks':-1.2,'regards':-1.4,'sincerely':-1.5,'attached':-1.1,
                'report':-1.3,'update':-0.8,'schedule':-1.4,'discuss':-1.2,
                'review':-1.0,'agenda':-1.6,'proposal':-1.2,
            }
            logit = -1.5
            seen  = set()
            for w in words:
                if w not in seen:
                    seen.add(w)
                    logit += spam_tokens.get(w, 0)
                    logit += ham_tokens.get(w, 0)

            exclaims  = text.count('!')
            caps_ratio= sum(1 for c in subj if c.isupper()) / max(len(subj), 1)
            url_count = text.lower().count('http')
            dollars   = text.count('$')

            logit += min(exclaims  * 0.3,  2.0)
            logit += min(caps_ratio * 4.0, 2.5)
            logit += min(url_count  * 0.8, 2.0)
            logit += min(dollars   * 0.6,  1.5)

            spam_prob  = 100 / (1 + math.exp(-logit))
            is_spam    = spam_prob >= 50
            confidence = min(99, 50 + abs(logit) * 8)

        return jsonify({
            'prediction':       'SPAM' if is_spam else 'NOT SPAM',
            'is_spam':          is_spam,
            'spam_probability': round(spam_prob, 2),
            'confidence':       round(confidence, 2),
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500