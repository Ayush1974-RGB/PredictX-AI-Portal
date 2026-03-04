from flask import Blueprint, request, jsonify
import os, math

fraud_bp  = Blueprint('fraud', __name__)
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

def calc_fraud(dist_home, dist_last, ratio, retailer, chip, pin, online):
    logit = -3.2
    if ratio < 1:       logit += -0.8
    elif ratio < 2:     logit += 0.2
    elif ratio < 3:     logit += 1.4
    elif ratio < 5:     logit += 2.8
    else:               logit += 4.2

    logDH = math.log1p(dist_home)
    if logDH < 1:       logit += -0.5
    elif logDH < 2:     logit += 0.3
    elif logDH < 3:     logit += 1.2
    elif logDH < 4:     logit += 2.1
    else:               logit += 3.5

    logDL = math.log1p(dist_last)
    if logDL < 1:       logit += -0.3
    elif logDL < 2:     logit += 0.4
    elif logDL < 3:     logit += 1.1
    else:               logit += 2.2

    logit += 1.3  if online   else -0.4
    logit += -1.1 if chip     else  0.8
    logit += -0.5 if retailer else  0.3
    logit += -0.3 if pin      else  0.1

    prob     = 100 / (1 + math.exp(-logit))
    is_fraud = prob >= 50
    risk     = 'HIGH' if prob >= 60 else ('MEDIUM' if prob >= 30 else 'LOW')
    return {'is_fraud': is_fraud, 'fraud_probability': prob, 'risk_level': risk,
            'prediction': 'FRAUD' if is_fraud else 'LEGITIMATE'}

@fraud_bp.route('/predict', methods=['POST'])
def predict():
    try:
        d         = request.get_json()
        dist_home = float(d.get('distance_from_home', 10))
        dist_last = float(d.get('distance_from_last_transaction', 1))
        ratio     = float(d.get('ratio_to_median_purchase_price', 1))
        retailer  = bool(d.get('repeat_retailer', 1))
        chip      = bool(d.get('used_chip', 1))
        pin       = bool(d.get('used_pin_number', 0))
        online    = bool(d.get('online_order', 0))

        try:
            import joblib, numpy as np
            feat_names = joblib.load(os.path.join(MODEL_DIR, 'fraud_features.pkl'))
            scaler     = joblib.load(os.path.join(MODEL_DIR, 'fraud_scaler.pkl'))
            model      = joblib.load(os.path.join(MODEL_DIR, 'fraud_model.pkl'))
            fm = {
                'distance_from_home': dist_home,
                'distance_from_last_transaction': dist_last,
                'ratio_to_median_purchase_price': ratio,
                'repeat_retailer': int(retailer),
                'used_chip': int(chip),
                'used_pin_number': int(pin),
                'online_order': int(online),
            }
            vec    = np.array([[fm[f] for f in feat_names]])
            scaled = scaler.transform(vec)
            pred   = model.predict(scaled)[0]
            proba  = model.predict_proba(scaled)[0]
            prob   = float(proba[1]) * 100
            is_fraud = bool(pred == 1)
            risk   = 'HIGH' if prob >= 60 else ('MEDIUM' if prob >= 30 else 'LOW')
            result = {'is_fraud': is_fraud, 'fraud_probability': prob,
                      'risk_level': risk, 'prediction': 'FRAUD' if is_fraud else 'LEGITIMATE'}
        except Exception:
            result = calc_fraud(dist_home, dist_last, ratio, retailer, chip, pin, online)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500