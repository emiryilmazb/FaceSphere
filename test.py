face_recognizer.py

import subprocess

while True:
    user_input = input("Press 't' to trigger face recognition process: ")
    if user_input.lower() == 't':
        subprocess.run(["python", "face_taker.py"])

face_taker.py
import subprocess

# Burada yüz tespiti işlemleri yapılır.

# Ardından eğitim işlemi başlatılır.
subprocess.run(["python", "face_train.py"])

# Eğitim tamamlandıktan sonra face_recognizer.py betiğini tekrar çağırır.
subprocess.run(["python", "face_recognizer.py"])

face_train.py
# Yüz eğitimi işlemleri yapılır.

# Eğitim tamamlandıktan sonra face_recognizer.py betiğini tekrar çağırır.
import subprocess
subprocess.run(["python", "face_recognizer.py"])