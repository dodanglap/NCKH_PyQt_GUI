import cv2
import os

status1 = 0

def recognize():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer_face.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Đọc tên từ file và loại bỏ khoảng trắng không cần thiết
    if not os.path.isfile("user.txt"):
        print("Error: User file not found.")
        return
    
    with open("user.txt", 'r') as file:
        names = [name.strip() for name in file.read().split(',')]
    
    print("Loaded names:", names)

    cam = cv2.VideoCapture(1)
    cam.set(3, 640)
    cam.set(4, 480)

    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)
    global status1

    while True:
        status = 0
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(int(minW), int(minH)))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            
            if confidence < 100:
                confidence = round(100 - confidence)
                # Kiểm tra xem id có hợp lệ không
                if id < len(names):
                    id = names[id]
                    cv2.putText(img, str(f"USER: {id}"), (x+5, y-5), font, 1, (255, 255, 255), 2)
                    print("User success")
                else:
                    id = "Unknown"
                    cv2.putText(img, str(id), (x+5, y-5), font, 1, (255, 0, 0), 2)
                cv2.putText(img, f"{confidence}%", (x+5, y+h-5), font, 1, (255, 255, 0), 1)
                
                if confidence > 50:
                    print("ID: ", id)
                    status += 1
                else:
                    status1 += 1
                    print(status1)
                break
            else:
                id = "Unknown"
                confidence = round(100 - confidence)
                cv2.putText(img, "Unknown", (x+5, y-5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, f"{round(100 - confidence)}%", (x+5, y+h-5), font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        if status != 0:
            print("Xác nhận thành công!")
            break
        if status1 == 100:
            break

        k = cv2.waitKey(10) & 0xff
        if k == 27:  # ESC để thoát
            break

    cam.release()
    cv2.destroyAllWindows()

def security():
    global status1
    if status1 == 100:
        status1 = 0
        return False
    else:
        status1 = 0
        return True

if __name__ == "__main__":
    recognize()
