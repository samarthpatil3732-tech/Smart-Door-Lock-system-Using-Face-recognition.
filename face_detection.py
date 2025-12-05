import cv2  #Used for camera access, face detection, and image processing.
import os #Provides functions to interact with the operating system.
import numpy as np #s used for mathematical operations, arrays, and matrix handling.
import smtplib #used for mathematical operations, arrays, and matrix handling.
import random
import serial #communication with Arduino
import time
import threading #running multiple tasks parallelly.
from email.message import EmailMessage #create structured email content with subject, body & attachments.
from playsound import playsound  # optional sound alert

# ===========================================================
# Arduino Connection
# ===========================================================
arduino = None
try:
    arduino = serial.Serial("COM5", 9600)
    time.sleep(2)
    print("[INFO] Arduino Connected!")
except:
    print("[WARNING] Arduino not detected! Running without hardware.")

# ===========================================================
# Haar Cascade + LBPH Recognizer
# ===========================================================
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()

dataset = r"C:\Users\samarth\Desktop\photo"
faces, labels = [], []
label_map, id = {}, 0

print("[INFO] Training images...")

for person in os.listdir(dataset):
    p = os.path.join(dataset, person)
    if os.path.isdir(p):
        label_map[id] = person
        for img in os.listdir(p):
            img_path = os.path.join(p, img)
            image = cv2.imread(img_path)
            if image is None: continue

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            rects = face_cascade.detectMultiScale(gray, 1.1, 5)

            for (x, y, w, h) in rects:
                crop = gray[y:y+h, x:x+w]
                crop = cv2.resize(crop, (200, 200))
                faces.append(crop)
                labels.append(id)

        id += 1

recognizer.train(faces, np.array(labels))
print("[INFO] Training Completed Successfully\n")

# ===========================================================
# Email Sender
# ===========================================================
def send_mail(receiver, img_path, message):
    email = EmailMessage()
    email['From'] = "abcyadav3732@gmail.com"
    email['To'] = receiver
    email['Subject'] = "Smart Door Alert"
    email.set_content(message)

    with open(img_path, "rb") as f:
        email.add_attachment(f.read(), maintype='image', subtype='jpg', filename="captured.jpg")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("abcyadav3732@gmail.com", "xctxhbqtfwhdxexy")  # Change password
        server.send_message(email)

    print("[EMAIL SENT SUCCESSFULLY]")

# ===========================================================
# Sound alert function (optional)
# ===========================================================
def play_alert():
    playsound("alert.wav")

#
# Camera Detection (10 seconds)

cap = cv2.VideoCapture(0)
otp_sent = False
authorized_detected = False  # Track if any authorized face is found
last_frame = None

start_time = time.time()
camera_duration = 10  # seconds

while True:
    if time.time() - start_time >= camera_duration:
        print("[INFO] Camera time expired.")
        break

    ret, frame = cap.read()
    if not ret:
        continue

    last_frame = frame.copy()  # store last frame for unmatched email
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_rect = face_cascade.detectMultiScale(gray, 1.3, 5)

    status = "Locked"

    for (x, y, w, h) in faces_rect:
        crop = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
        label, conf = recognizer.predict(crop)

        # Authorized face
        if conf < 60:
            authorized_detected = True
            name = label_map[label]
            cv2.putText(frame, f"{name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            status = "Face Valid"

            if not otp_sent:
                otp_sent = True
                correct_otp = str(random.randint(100000, 999999))
                img = "authorized.jpg"
                cv2.imwrite(img, frame)
                send_mail("YOUR_EMAIL@gmail.com", img, f"Face Verified\nOTP = {correct_otp}")

                user = input("\nEnter OTP: ")
                if user == correct_otp:
                    print("\n✔ OTP Correct → Door Unlocked")
                    status = "Unlocked"
                    if arduino: arduino.write(b'U')
                else:
                    print("\n✘ Wrong OTP")
                    if arduino: arduino.write(b'L')

        # Unknown face
        else:
            cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Display
    color = (0, 255, 0) if status == "Unlocked" else (0, 0, 255)
    cv2.rectangle(frame, (20, 20), (260, 100), color, -1)
    cv2.putText(frame, status, (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow("Smart Door", frame)
    if cv2.waitKey(1) == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()

# ===========================================================
# After 10 seconds, send email if no authorized face detected
# ===========================================================
if not authorized_detected:
    img_name = "intruder.jpg"
    cv2.imwrite(img_name, last_frame)

    # Optional sound alert
    threading.Thread(target=play_alert, daemon=True).start()

    send_mail("YOUR_EMAIL@gmail.com", img_name,
              "⚠ Unauthorized Access Detected\nImage Attached.")

    print("[⚠ Unauthorized Access Email Sent]")


