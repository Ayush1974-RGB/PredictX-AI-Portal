from flask import Blueprint, request, jsonify
import os, math

spam_bp   = Blueprint('spam', __name__)
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

def calc_spam(subject, body):
    text  = f'{subject} {body}'.lower()
    words = text.split()
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
        'review':-1.0,'agenda':-1.6,'proposal':-1.2,'hello':-0.6,
        'hi':-0.5,'lunch':-1.0,'friday':-0.7,'everyone':-0.6,
    }
    logit = -1.5
    seen  = set()
    for w in words:
        if w not in seen:
            seen.add(w)
            logit += spam_tokens.get(w, 0)
            logit += ham_tokens.get(w, 0)

    logit += min((text.count('!'))      * 0.3,  2.0)
    logit += min((len([c for c in subject if c.isupper()]) / max(len(subject),1)) * 4.0, 2.5)
    logit += min((text.count('http'))   * 0.8,  2.0)
    logit += min((text.count('$'))      * 0.6,  1.5)

    if len(words) < 20 and logit < 0:
        logit -= 0.5

    prob    = 100 / (1 + math.exp(-logit))
    is_spam = prob >= 50
    conf    = min(99, 50 + abs(logit) * 8)
    return {'prediction': 'SPAM' if is_spam else 'NOT SPAM',
            'is_spam': is_spam, 'spam_probability': prob, 'confidence': conf}

@spam_bp.route('/predict', methods=['POST'])
def predict():
    try:
        d       = request.get_json()
        subject = d.get('subject', '')
        body    = d.get('body', '')
        text    = f'{subject} {body}'.strip()
        if not text:
            return jsonify({'error': 'Email content required'}), 400

        try:
            import joblib
            model = joblib.load(os.path.join(MODEL_DIR, 'spam_model.pkl'))
            pred  = model.predict([text])[0]
            proba = model.predict_proba([text])[0]
            is_spam   = bool(pred == 1)
            prob      = float(proba[1]) * 100
            conf      = float(max(proba)) * 100
            result    = {'prediction': 'SPAM' if is_spam else 'NOT SPAM',
                         'is_spam': is_spam, 'spam_probability': prob, 'confidence': conf}
        except Exception:
            result = calc_spam(subject, body)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500