import cv2
import os

def collect(face_id):
    cam = cv2.VideoCapture(1)
    cam.set(3, 640) 
    cam.set(4, 480)
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Lưu tên vào txt
    with open("user.txt", "a") as f:
        f.writelines(f"{face_id}\n")
        
    count = 0
    
    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            count += 1
            cv2.imwrite("data_face/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
        cv2.imshow('image', img)

        k = cv2.waitKey(100) & 0xff
        if k == 27 or count >= 200:  # ESC để thoát hoặc thu thập đủ 200 ảnh
            break

    cam.release()
    cv2.destroyAllWindows()
    print(f"Collected {count} face images for ID {face_id}.")
    
    print("Collect face successfully!")
    with open("user.txt", "a") as f:
        f.write(f"{face_id}\n")
    f.close()
if __name__ == "__main__":
    face_id = input("Enter user ID: ")
    
    collect(face_id)


