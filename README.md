# FaceSphere 🛡️👤

**FaceSphere** is an advanced Flask-based face recognition and liveness detection system. Leveraging DeepFace and Dlib libraries, it not only matches faces but also verifies the physical presence of a user by tracking head movements (turn left/right), making it a robust solution for smart door locks, secure entry points, and attendance systems.

## 🚀 Features

- **Real-Time Face Recognition:** Analyzes webcam feed and matches faces against registered users.
- **Liveness Detection:** Prevents photo spoofing by prompting the user to perform random or sequential head movements (e.g., "turn left", "turn right").
- **Admin Panel:** A web interface for authorized personnel to add/remove users and view logs.
- **Security Logs:** Unrecognized faces and unauthorized access attempts are saved to the "Unknown_USER" folder and logged in the database.
- **SQLite Database:** User details and access logs are stored in a local SQLite database.

## 📂 Project Structure

```
FaceSphere/
├── app.py                # Application entry point & factory
├── config.py             # Configuration settings
├── extensions.py         # Flask extensions (SQLAlchemy)
├── shared_state.py       # Global state management
├── database_models.py    # Database models (User, AccessLog)
├── face_utils.py         # Face recognition & angle calculation utilities
├── routes/               # Blueprint routes
│   ├── main_routes.py    # Core application logic & video feed
│   └── admin_routes.py   # Admin panel & user management
├── requirements.txt      # Python dependencies
├── database.db           # SQLite database (auto-generated)
├── models/               # Dlib model files
│   └── shape_predictor_68_face_landmarks.dat
├── static/               # CSS & JS files
├── templates/            # HTML templates
├── users/                # Registered user photos
└── docs/                 # Project documentation & reports
```

## 🛠️ Installation

### Requirements

- Python 3.10+ (Python 3.12.3 recommended)
- Webcam
- CMake (required for compiling dlib)

### Step-by-Step Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/username/FaceSphere.git
    cd FaceSphere
    ```

2.  **Create and activate a virtual environment:**

    - **Windows:**
      ```bash
      python -m venv venv
      .\venv\Scripts\activate
      ```
    - **Linux/Mac:**
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    _Note: If you encounter issues installing `dlib`, ensure you have a C++ compiler and CMake installed on your system._

4.  **Run the application:**
    ```bash
    python app.py
    ```

## 💻 Usage

1.  Once the application is running, open your browser and navigate to `http://127.0.0.1:5000/`.
2.  The webcam will activate, and the system will start searching for faces.
3.  **Adding Users (Admin):**
    - Go to `/admin_panel` (Default credentials: `admin` / `admin` - change this for production!).
    - Use the "Add User" section to enter details.
    - Place clear photos of the user in `users/Name_Surname` folder.
4.  **Verification Process:**
    - When a face is recognized, follow the on-screen instructions (e.g., "Please turn left").
    - Upon successful verification of both face and movement, a "Door is opening" message will appear.

## 📝 Notes

- Proper lighting is crucial for optimal face recognition performance.
- The `database.db` file will be automatically created upon the first run.
- Ensure `shape_predictor_68_face_landmarks.dat` is present in the `models/` directory.

## 🔒 Security Warning

This project is intended as a prototype/demo. Before deploying in a production environment, it is strongly recommended to enhance the admin panel security (hashing passwords, session management) and enforce HTTPS.

## 📄 License

This project is provided under the license specified in the [LICENSE](LICENSE) file.
