import cv2
import numpy as np
from PIL import Image
import os

def training(path):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L')  # Chuyển ảnh sang grayscale
        img_numpy = np.array(PIL_img, 'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y+h, x:x+w])
            ids.append(id)

    if len(faceSamples) == 0:
        print("No faces found in images.")
        return

    recognizer.train(faceSamples, np.array(ids))
    
    # Tạo thư mục trainer nếu chưa có
    if not os.path.exists('trainer'):
        os.makedirs('trainer')

    recognizer.write('trainer/trainer_face.yml')
    print("Training completed successfully!")

if __name__ == "__main__":
    training('data_face')  # Đảm bảo thư mục này chứa các ảnh huấn luyện
