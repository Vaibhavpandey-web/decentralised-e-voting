import os
import cv2
import json
import base64
import shutil
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS  
import face_recognition
from scipy.spatial import distance as dist
import dlib

app = Flask(__name__)
# Force CORS to accept requests from your local Vue frontend instances
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURATION ---
FACE_DB_DIR = "face_db"
VOTED_LEDGER = "voted.json"
TOLERANCE = 0.45

# Ensure storage layers exist cleanly on startup
os.makedirs(FACE_DB_DIR, exist_ok=True)
if not os.path.exists(VOTED_LEDGER) or os.stat(VOTED_LEDGER).st_size == 0:
    with open(VOTED_LEDGER, "w") as f:
        json.dump([], f)

# Initialize dlib detectors
detector = dlib.get_frontal_face_detector()
try:
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
except RuntimeException:
    print("Warning: shape_predictor_68_face_landmarks.dat not found in server directory.")

def calculate_ear(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def calculate_mar(mouth):
    A = dist.euclidean(mouth[1], mouth[7])  
    B = dist.euclidean(mouth[2], mouth[6])  
    C = dist.euclidean(mouth[3], mouth[5])  
    D = dist.euclidean(mouth[0], mouth[4])  
    return (A + B + C) / (2.0 * D)

def check_head_turn(coords, direction):
    nose_tip = coords[30]
    left_jaw = coords[2]
    right_jaw = coords[14]
    ratio = dist.euclidean(nose_tip, left_jaw) / dist.euclidean(nose_tip, right_jaw)
    if direction == "turn_right" and ratio > 1.5: return True
    if direction == "turn_left" and ratio < 0.7: return True
    return False

def decode_base64_frame(base64_string):
    img_data = base64.b64decode(base64_string.split(",")[1] if "," in base64_string else base64_string)
    np_arr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

# --- 1. BIOMETRIC REGISTRATION ENDPOINT ---
@app.route('/register', methods=['POST', 'OPTIONS'])
def register_voter():
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        data = request.json
        roll_no = data.get('roll_no')
        img = decode_base64_frame(data.get('image'))
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        encodings = face_recognition.face_encodings(rgb_img)
        if not encodings:
            return jsonify({"status": "error", "message": "No face detected. Adjust lighting."}), 400
        
        np.save(os.path.join(FACE_DB_DIR, f"{roll_no}.npy"), encodings[0])
        return jsonify({"status": "success", "message": f"Roll No {roll_no} registered successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 2. BIOMETRIC VERIFICATION ENDPOINT ---
@app.route('/verify', methods=['POST', 'OPTIONS'])
def verify_voter():
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        data = request.json
        roll_no = data.get('roll_no')
        frames_b64 = data.get('frames') 
        challenge = data.get('challenge') 

        with open(VOTED_LEDGER, "r") as f:
            voted_list = json.load(f)
        if roll_no in voted_list:
            return jsonify({"status": "error", "message": "ALREADY_VOTED"}), 403

        db_path = os.path.join(FACE_DB_DIR, f"{roll_no}.npy")
        if not os.path.exists(db_path):
            return jsonify({"status": "error", "message": "UNREGISTERED_ROLL_NO"}), 404
            
        registered_encoding = np.load(db_path)
        challenge_passed, identity_matched, action_frames = False, False, 0

        for b64_frame in frames_b64:
            img = decode_base64_frame(b64_frame)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if not identity_matched:
                encodings = face_recognition.face_encodings(rgb_img)
                if encodings and face_recognition.face_distance([registered_encoding], encodings[0])[0] < TOLERANCE:
                    identity_matched = True

            faces = detector(gray, 0)
            for face in faces:
                shape = predictor(gray, face)
                coords = np.zeros((68, 2), dtype="int")
                for i in range(0, 68): coords[i] = (shape.part(i).x, shape.part(i).y)
                
                if challenge == "blink":
                    if (calculate_ear(coords[42:48]) + calculate_ear(coords[36:42])) / 2.0 < 0.25: action_frames += 1
                elif challenge == "smile":
                    if calculate_mar(coords[60:68]) > 0.45: action_frames += 1
                elif challenge in ["turn_left", "turn_right"]:
                    if check_head_turn(coords, challenge): action_frames += 1

                if action_frames >= 1: challenge_passed = True

        if not identity_matched: return jsonify({"status": "error", "message": "Identity Mismatch."}), 401
        if not challenge_passed: return jsonify({"status": "error", "message": f"Failed Liveness Challenge ({challenge})."}), 401

        return jsonify({"status": "success", "message": "Identity and Liveness Verified."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 3. MARK VOTED LEDGER ENDPOINT ---
@app.route('/mark_voted', methods=['POST', 'OPTIONS'])
def mark_voted():
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        roll_no = request.json.get('roll_no')
        with open(VOTED_LEDGER, "r+") as f:
            voted_list = json.load(f)
            if roll_no not in voted_list:
                voted_list.append(roll_no)
                f.seek(0)
                json.dump(voted_list, f)
                f.truncate()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 4. FIXED RESTORED ADMIN WIPE DATA ENDPOINT ---
# This endpoint listens to common admin endpoints (/wipe_data, /clear_data, /reset_system)
@app.route('/wipe_data', methods=['POST', 'OPTIONS'])
@app.route('/clear_data', methods=['POST', 'OPTIONS'])
@app.route('/resetElection', methods=['POST', 'OPTIONS'])
def wipe_system_data():
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        # 1. Clear out the biometrics database directory
        if os.path.exists(FACE_DB_DIR):
            shutil.rmtree(FACE_DB_DIR)
        os.makedirs(FACE_DB_DIR, exist_ok=True)

        # 2. Reset local JSON tracking ledger back to a valid blank array
        with open(VOTED_LEDGER, "w") as f:
            json.dump([], f)

        return jsonify({
            "status": "success", 
            "message": "System data wiped successfully. All roll numbers and face mappings cleared."
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Admin wipe failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)