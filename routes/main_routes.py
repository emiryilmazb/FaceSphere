from flask import Blueprint, render_template, Response, jsonify
import cv2
import os
import time
import face_utils
import shared_state

bp = Blueprint('main', __name__)


def process_frame(frame, user_images_folder):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_utils.detector(gray)

    if len(faces) == 0:
        shared_state.current_state["user_name"] = "Unknown"
        shared_state.current_state["state"] = "initial"
        shared_state.current_state["message"] = "No face detected, restarting process"
        return frame, None, None

    for face in faces:
        landmarks = face_utils.predictor(gray, face)
        angle = face_utils.get_face_turn_angle(landmarks)
        shared_state.current_state["angle"] = angle

        # Capture the face region
        x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

        # Ensure coordinates are within frame bounds
        h, w, _ = frame.shape
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        if x2 <= x1 or y2 <= y1:
            continue  # Skip invalid faces

        face_img = frame[y1:y2, x1:x2]

        # Save the captured face image as temp.jpg
        temp_image_path = "temp.jpg"
        cv2.imwrite(temp_image_path, face_img)

        # Verify face against the user images
        verified_user_name = None
        if os.path.exists(user_images_folder):
            for user in os.listdir(user_images_folder):
                user_folder = os.path.join(user_images_folder, user)
                if os.path.isdir(user_folder) and user != "Unknown_USER":
                    verified, user_name = face_utils.verify_face(
                        temp_image_path, user_folder)
                    if verified:
                        verified_user_name = user_name
                        shared_state.current_state["user_name"] = user_name
                        return frame, user_name, angle

        if not verified_user_name:
            # Check in Unknown_USER folder
            unknown_user_folder = os.path.join(
                user_images_folder, "Unknown_USER")
            if not os.path.exists(unknown_user_folder):
                os.makedirs(unknown_user_folder)

            verified, _ = face_utils.verify_face(
                temp_image_path, unknown_user_folder)
            if not verified:
                face_utils.save_unrecognized_face(
                    temp_image_path, unknown_user_folder)

    return frame, None, None


def gen(camera):
    state = "initial"
    verified_user_name = None
    temp_image_path = "temp.jpg"
    door_open_time = None

    # Ensure users directory exists
    if not os.path.exists("users"):
        os.makedirs("users")

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
                    shared_state.current_state["state"] = "turn_left"
                    shared_state.current_state["message"] = "Face recognized, please turn left"
                    state = "turn_left"

            elif state == "turn_left":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_utils.detector(gray)
                if len(faces) == 0:
                    shared_state.current_state["user_name"] = "Unknown"
                    shared_state.current_state["state"] = "initial"
                    shared_state.current_state["message"] = "No face detected, restarting process"
                    state = "initial"
                    continue

                # Use the first face detected
                face = faces[0]
                landmarks = face_utils.predictor(gray, face)
                angle = face_utils.get_face_turn_angle(landmarks)

                if angle > 20:  # Adjust the angle threshold as needed
                    x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

                    h, w, _ = frame.shape
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(w, x2)
                    y2 = min(h, y2)

                    face_img = frame[y1:y2, x1:x2]
                    cv2.imwrite(temp_image_path, face_img)

                    user_folder = os.path.join("users", verified_user_name)
                    verified, user_name = face_utils.verify_face(
                        temp_image_path, user_folder)

                    if verified and user_name == verified_user_name:
                        shared_state.current_state["state"] = "turn_right"
                        shared_state.current_state["message"] = "Face recognized, please turn right"
                        state = "turn_right"
                    else:
                        shared_state.current_state["state"] = "initial"
                        shared_state.current_state["user_name"] = "Unknown"
                        shared_state.current_state["message"] = "Face not recognized, starting over"
                        state = "initial"

            elif state == "turn_right":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_utils.detector(gray)
                if len(faces) == 0:
                    shared_state.current_state["user_name"] = "Unknown"
                    shared_state.current_state["state"] = "initial"
                    shared_state.current_state["message"] = "No face detected, restarting process"
                    state = "initial"
                    continue

                face = faces[0]
                landmarks = face_utils.predictor(gray, face)
                angle = face_utils.get_face_turn_angle(landmarks)

                if angle < -20:  # Adjust the angle threshold as needed
                    x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

                    h, w, _ = frame.shape
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(w, x2)
                    y2 = min(h, y2)

                    face_img = frame[y1:y2, x1:x2]
                    cv2.imwrite(temp_image_path, face_img)

                    user_folder = os.path.join("users", verified_user_name)
                    verified, user_name = face_utils.verify_face(
                        temp_image_path, user_folder)

                    if verified and user_name == verified_user_name:
                        print(f"Door is opening for {user_name}")
                        shared_state.current_state["state"] = "door_open"
                        shared_state.current_state[
                            "message"] = f"Door is opening for {user_name}"
                        state = "door_open"
                        door_open_time = time.time()
                    else:
                        shared_state.current_state["state"] = "initial"
                        shared_state.current_state["message"] = "Face not recognized, starting over"
                        shared_state.current_state["user_name"] = "Unknown"
                        state = "initial"
            elif shared_state.current_state["state"] == "door_open":
                # Check if 10 seconds have elapsed since the door opened
                if time.time() - door_open_time >= 10:
                    shared_state.current_state["state"] = "initial"
                    shared_state.current_state["user_name"] = "Unknown"
                    shared_state.current_state["message"] = "Face not recognized, starting over"
                    state = "initial"

            ret, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

        except Exception as e:
            print(f"Error in gen loop: {e}")
            time.sleep(1)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/state')
def get_state():
    return jsonify(shared_state.current_state)


@bp.route('/angle')
def get_angle():
    return jsonify({"angle": shared_state.current_state["angle"]})


@bp.route('/video_feed')
def video_feed():
    return Response(gen(cv2.VideoCapture(0)), mimetype='multipart/x-mixed-replace; boundary=frame')
