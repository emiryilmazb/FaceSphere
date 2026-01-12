import cv2
import os
import numpy as np
import dlib
from deepface import DeepFace

# Load dlib's face detector and predictor
# Ensure the model file exists at this path
predictor_path = "models/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

# Model configuration
model_name = "VGG-Face"
treshold = 0.55


def get_face_turn_angle(landmarks):
    """
    Calculate face orientation based on the nose and eyes.
    """
    left_eye_center = np.array([landmarks.part(36).x, landmarks.part(36).y])
    right_eye_center = np.array([landmarks.part(45).x, landmarks.part(45).y])
    nose_tip = np.array([landmarks.part(30).x, landmarks.part(30).y])

    eyes_center = (left_eye_center + right_eye_center) / 2
    nose_vector = nose_tip - eyes_center

    angle = np.degrees(np.arctan2(nose_vector[0], nose_vector[1]))
    return angle


def verify_face(temp_image_path, user_folder):
    """
    Verify if the face in temp_image_path matches any face in user_folder.
    """
    print(f"Verifying face against folder: {user_folder}")
    if not os.path.exists(user_folder):
        return False, None

    for img_path in os.listdir(user_folder):
        img_full_path = os.path.join(user_folder, img_path)
        # Skip non-image files if necessary, or let deepface handle errors
        print(f"Comparing with image: {img_full_path}")
        try:
            result = DeepFace.verify(
                img1_path=temp_image_path,
                img2_path=img_full_path,
                model_name=model_name,
                enforce_detection=False
            )
            print(f"Verification result: {result}")
            if result["verified"] and result["distance"] < treshold:
                return True, os.path.basename(user_folder)
        except ValueError as ve:
            print(f"Verification error with {img_full_path}: {ve}")
        except Exception as e:
            print(f"Unexpected error with {img_full_path}: {e}")

    return False, None


def save_unrecognized_face(temp_image_path, unknown_user_folder):
    """
    Save the unrecognized face image to the unknown_user_folder.
    """
    if not os.path.exists(unknown_user_folder):
        os.makedirs(unknown_user_folder)

    img_name = f"unknown_{len(os.listdir(unknown_user_folder)) + 1}.jpg"
    save_path = os.path.join(unknown_user_folder, img_name)

    image = cv2.imread(temp_image_path)
    if image is not None:
        cv2.imwrite(save_path, image)
        print(f"Unrecognized face saved to {save_path}")
    else:
        print(f"Failed to load image from {temp_image_path}")
