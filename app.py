from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

class Camera:
    def __init__(self, camera_id):
        self.camera = cv2.VideoCapture(camera_id)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def get_frame(self):
        success, frame = self.camera.read()
        if not success:
            print("Cannot reach the camera")
            return None
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, "Door is opening..", (10, 40), font, 1.2, (0, 150, 0), 2, cv2.LINE_AA)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

# Create instances of Camera class for each camera
cameras = {'0': Camera(0), '1': Camera(1), '2': Camera(2), '3': Camera(3)}

@app.route('/')
def index():
    return render_template('index.html', cameras=cameras)

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    return Response(stream_camera(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

def stream_camera(camera_id):
    while True:
        frame = cameras[str(camera_id)].get_frame()
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
