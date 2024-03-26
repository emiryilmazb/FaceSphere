import cv2
import os
import time

def capture_images(person_name, num_images=10):
    save_dir = os.path.join("user", person_name)
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)

    count = 0

    while count < num_images:
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture image")
            continue

        cv2.imshow('Capture Images', frame)

        image_path = os.path.join(save_dir, f"{person_name}_{count}.jpg")
        cv2.imwrite(image_path, frame)
        time.sleep(1)
        count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    person_name = input("Enter the person's name: ")

    capture_images(person_name,10)