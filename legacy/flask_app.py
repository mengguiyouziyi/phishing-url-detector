#importing required libraries

from flask import Flask, request, render_template, jsonify
import numpy as np
import pandas as pd
from sklearn import metrics
import warnings
import pickle
import threading
import time
warnings.filterwarnings('ignore')
from feature import FeatureExtraction

file = open("pickle/model.pkl","rb")
gbc = pickle.load(file)
file.close()

app = Flask(__name__)

def extract_features_with_timeout(url, timeout=15):
    """Extract features with timeout to prevent hanging"""
    result = {'features': None, 'error': None}

    def target():
        try:
            obj = FeatureExtraction(url)
            features = obj.getFeaturesList()
            result['features'] = features
        except Exception as e:
            result['error'] = str(e)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        result['error'] = "Feature extraction timed out"

    return result

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "POST":
        try:
            url = request.form.get("url")

            if not url or not url.startswith(('http://', 'https://')):
                return jsonify({'error': 'Invalid URL format'})

            # Extract features with timeout
            result = extract_features_with_timeout(url)

            if result['error']:
                return jsonify({'xx': -2, 'error': result['error'], 'url': url})

            features = result['features']
            if not features or len(features) != 30:
                return jsonify({'xx': -3, 'error': 'Invalid feature extraction', 'url': url})

            x = np.array(features).reshape(1,30)

            y_pred = gbc.predict(x)[0]
            y_pro_phishing = gbc.predict_proba(x)[0,0]
            y_pro_non_phishing = gbc.predict_proba(x)[0,1]

            # Feature names for detailed analysis
            feature_names = [
                'UsingIP', 'LongURL', 'ShortURL', 'Symbol@', 'Redirecting//',
                'PrefixSuffix-', 'SubDomains', 'HTTPS', 'DomainRegLen', 'Favicon',
                'NonStdPort', 'HTTPSDomainURL', 'RequestURL', 'AnchorURL', 'LinksInScriptTags',
                'ServerFormHandler', 'InfoEmail', 'AbnormalURL', 'WebsiteForwarding',
                'StatusBarCust', 'DisableRightClick', 'UsingPopupWindow', 'IframeRedirection',
                'AgeofDomain', 'DNSRecording', 'WebsiteTraffic', 'PageRank', 'GoogleIndex',
                'LinksPointingToPage', 'StatsReport'
            ]

            # Create feature analysis
            feature_analysis = []
            for i, (name, value) in enumerate(zip(feature_names, features)):
                interpretation = ""
                if value == 1:
                    interpretation = "安全指标"
                elif value == 0:
                    interpretation = "可疑指标"
                elif value == -1:
                    interpretation = "危险指标"

                feature_analysis.append({
                    'name': name,
                    'value': value,
                    'interpretation': interpretation
                })

            # Risk assessment
            risk_factors = []
            if features[3] == -1: risk_factors.append("包含@符号")
            if features[4] == -1: risk_factors.append("URL重定向")
            if features[5] == -1: risk_factors.append("前缀后缀可疑")
            if features[7] == -1: risk_factors.append("未使用HTTPS")
            if features[12] == -1: risk_factors.append("可疑请求URL")
            if features[14] == -1: risk_factors.append("脚本标签异常")
            if features[20] == -1: risk_factors.append("禁用右键点击")
            if features[22] == -1: risk_factors.append("弹窗警告")

            safety_factors = []
            if features[7] == 1: safety_factors.append("使用HTTPS加密")
            if features[8] == 1: safety_factors.append("域名注册时间较长")
            if features[23] == 1: safety_factors.append("域名年龄较大")
            if features[25] == 1: safety_factors.append("网站流量正常")
            if features[26] == 1: safety_factors.append("PageRank良好")
            if features[27] == 1: safety_factors.append("已被Google索引")

            # Return enhanced analysis
            xx = round(y_pro_non_phishing, 2)
            return jsonify({
                'xx': xx,
                'url': url,
                'prediction': int(y_pred),
                'confidence': y_pro_non_phishing if y_pred == 1 else y_pro_phishing,
                'phishing_prob': y_pro_phishing,
                'non_phishing_prob': y_pro_non_phishing,
                'feature_analysis': feature_analysis,
                'risk_factors': risk_factors,
                'safety_factors': safety_factors,
                'total_features': len(features),
                'risk_score': sum(1 for f in features if f == -1),
                'safety_score': sum(1 for f in features if f == 1)
            })

        except Exception as e:
            return jsonify({'xx': -4, 'error': str(e), 'url': url})

    return jsonify({'error': 'Invalid request method'})

@app.route("/api/health")
def health():
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)