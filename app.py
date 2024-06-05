from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, session
import cv2
import os
import numpy as np
import dlib
from deepface import DeepFace
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = 'FaceSphere'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)

# Load dlib's face detector and predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")  # Update with the correct path

# Global variable to store state information
current_state = {
    "state": "initial",
    "user_name": None,
    "angle": None,
    "message": "Initializing..."
}

# Model name for face recognition
model_name = "VGG-Face"
treshold = 0.55

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    department = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    entry_time = db.Column(db.String(20))
    exit_time = db.Column(db.String(20))
    photo_location = db.Column(db.String(100))

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_time = db.Column(db.String(20))

# Helper function to calculate face orientation based on the nose and eyes
def get_face_turn_angle(landmarks):
    left_eye_center = np.array([landmarks.part(36).x, landmarks.part(36).y])
    right_eye_center = np.array([landmarks.part(45).x, landmarks.part(45).y])
    nose_tip = np.array([landmarks.part(30).x, landmarks.part(30).y])
    
    eyes_center = (left_eye_center + right_eye_center) / 2
    nose_vector = nose_tip - eyes_center
    
    angle = np.degrees(np.arctan2(nose_vector[0], nose_vector[1]))
    return angle

# def unauthorized_access():
#     try:
#         # Get the current time
#         attempt_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
#         # Create a new AccessLog instance and add it to the database
#         new_log = AccessLog(attempt_time=attempt_time)
#         db.session.add(new_log)
        
#         # Commit the changes to the database
#         db.session.commit()
        
#         # Return a response indicating successful logging
#         return jsonify({'success': True, 'message': 'Unauthorized Access Logged!'})
    
#     except Exception as e:
#         # Handle any errors gracefully
#         db.session.rollback()  # Rollback changes in case of error
#         return jsonify({'success': False, 'message': str(e)})




def verify_face(temp_image_path, user_folder):
    print(f"Verifying face against folder: {user_folder}")
    for img_path in os.listdir(user_folder):
        img_full_path = os.path.join(user_folder, img_path)
        print(f"Comparing with image: {img_full_path}")
        try:
            result = DeepFace.verify(img1_path=temp_image_path, img2_path=img_full_path, model_name=model_name, enforce_detection=False)
            print(f"Verification result: {result}")
            if result["verified"] and result["distance"] < treshold:
                return True, os.path.basename(user_folder)
        except ValueError as ve:
            print(f"Verification error with {img_full_path}: {ve}")
    return False, None

def save_unrecognized_face(temp_image_path, unknown_user_folder):
    img_name = f"unknown_{len(os.listdir(unknown_user_folder)) + 1}.jpg"
    save_path = os.path.join(unknown_user_folder, img_name)
    cv2.imwrite(save_path, cv2.imread(temp_image_path))
    print(f"Unrecognized face saved to {save_path}")

def process_frame(frame, user_images_folder):
    global current_state

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    print(f"Detected {len(faces)} faces")

    if len(faces) == 0:
        current_state["user_name"] = "Unknown"
        current_state["state"] = "initial"
        current_state["message"] = "No face detected, restarting process"
        return frame, None, None

    for face in faces:
        landmarks = predictor(gray, face)
        angle = get_face_turn_angle(landmarks)
        print(f"Face turn angle: {angle}")
        current_state["angle"] = angle

        # Capture the face region
        x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
        face_img = frame[y1:y2, x1:x2]

        # Save the captured face image as temp.jpg
        temp_image_path = "temp.jpg"
        cv2.imwrite(temp_image_path, face_img)
        print(f"Saved face image to {temp_image_path}")

        # Verify face against the user images
        verified_user_name = None
        for user in os.listdir(user_images_folder):
            user_folder = os.path.join(user_images_folder, user)
            if os.path.isdir(user_folder) and user != "Unknown_USER":
                verified, user_name = verify_face(temp_image_path, user_folder)
                if verified:
                    verified_user_name = user_name
                    current_state["user_name"] = user_name
                    return frame, user_name, angle

        if not verified_user_name:
            
            # Check in Unknown_USER folder
            unknown_user_folder = os.path.join(user_images_folder, "Unknown_USER")
            if not os.path.exists(unknown_user_folder):
                os.makedirs(unknown_user_folder)
            
            verified, _ = verify_face(temp_image_path, unknown_user_folder)
            if not verified:
                print("Face is not recognized")
                # unauthorized_access()

                save_unrecognized_face(temp_image_path, unknown_user_folder)
                
    return frame, None, None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/state')
def get_state():
    return jsonify(current_state)

@app.route('/angle')
def get_angle():
    return jsonify({"angle": current_state["angle"]})

def gen(camera):
    global current_state
    state = "initial"
    verified_user_name = None
    temp_image_path = "temp.jpg"

    door_open_time = None

    while True:
        try:
            ret, frame = camera.read()
            if not ret:
                print("Failed to grab frame")
                break

            if state == "initial":
                frame, user_name, angle = process_frame(frame, "users")
                if user_name:
                    print(f"Verified user: {user_name}")
                    verified_user_name = user_name
                    current_state["state"] = "turn_left"
                    current_state["message"] = "Face recognized, please turn left"
                    state = "turn_left"

            elif state == "turn_left":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)
                if len(faces) == 0:
                    current_state["user_name"] = "Unknown"
                    current_state["state"] = "initial"
                    current_state["message"] = "No face detected, restarting process"
                    state = "initial"
                    continue
                landmarks = predictor(gray, faces[0])
                angle = get_face_turn_angle(landmarks)
                print(f"Left turn angle: {angle}")
                if angle > 20:  # Adjust the angle threshold as needed
                    x1, y1, x2, y2 = faces[0].left(), faces[0].top(), faces[0].right(), faces[0].bottom()
                    face_img = frame[y1:y2, x1:x2]
                    cv2.imwrite(temp_image_path, face_img)
                    verified, user_name = verify_face(temp_image_path, os.path.join("users", verified_user_name))
                    if verified and user_name == verified_user_name:
                        current_state["state"] = "turn_right"
                        current_state["message"] = "Face recognized, please turn right"
                        state = "turn_right"
                    else:
                        current_state["state"] = "initial"
                        current_state["user_name"] = "Unknown"
                        current_state["message"] = "Face not recognized, starting over"
                        state = "initial"

            elif state == "turn_right":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)
                if len(faces) == 0:
                    current_state["user_name"] = "Unknown"
                    current_state["state"] = "initial"
                    current_state["message"] = "No face detected, restarting process"
                    state = "initial"
                    continue

                landmarks = predictor(gray, faces[0])
                angle = get_face_turn_angle(landmarks)
                print(f"Right turn angle: {angle}")
                if angle < -20:  # Adjust the angle threshold as needed
                    x1, y1, x2, y2 = faces[0].left(), faces[0].top(), faces[0].right(), faces[0].bottom()
                    face_img = frame[y1:y2, x1:x2]
                    cv2.imwrite(temp_image_path, face_img)
                    verified, user_name = verify_face(temp_image_path, os.path.join("users", verified_user_name))
                    if verified and user_name == verified_user_name:
                        print(f"Door is opening for {user_name}")
                        current_state["state"] = "door_open"
                        current_state["message"] = f"Door is opening for {user_name}"
                        state = "door_open"
                        door_open_time = time.time() 
                    else:
                        current_state["state"] = "initial"
                        current_state["message"] = "Face not recognized, starting over"
                        current_state["user_name"] = "Unknown"
                        state = "initial"
            elif current_state["state"] == "door_open":
                # Check if 5 seconds have elapsed since the door opened
                if time.time() - door_open_time >= 10:
                    current_state["state"] = "initial"
                    current_state["user_name"] = "Unknown"
                    current_state["message"] = "Face not recognized, starting over"
                    state = "initial"

            ret, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

        except Exception as e:
            raise e

@app.route('/video_feed')
def video_feed():
    return Response(gen(cv2.VideoCapture(0)), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/admin_panel')
def admin_panel():
    if 'logged_in' in session and session['logged_in']:
        users = User.query.all()
        unauthorized_logs = AccessLog.query.all()
        return render_template('admin_panel.html', users=users, unauthorized_logs=unauthorized_logs)
    else:
        return redirect(url_for('index'))

@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if username == 'admin' and password == 'admin':
        session['logged_in'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department = request.form['department']
        phone_number = request.form['phone_number']
        entry_time = request.form['entry_time']
        exit_time = request.form['exit_time']
        photo_location = request.form['photo_location']

        new_user = User(first_name=first_name, last_name=last_name, department=department,
                        phone_number=phone_number, entry_time=entry_time, exit_time=exit_time,
                        photo_location=photo_location)
        db.session.add(new_user)
        db.session.commit()
    return jsonify({'success': True})

@app.route('/remove_user', methods=['POST'])
def remove_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user_to_remove = User.query.get(user_id)

        db.session.delete(user_to_remove)
        db.session.commit()

    return jsonify({'success': True})


if __name__ == "__main__":
    app.run(debug=True)
