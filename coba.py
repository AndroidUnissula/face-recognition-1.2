import cv2

face = cv2.CascadeClassifier('face-detect.xml')
eye = cv2.CascadeClassifier('eye-detect.xml')

video = cv2.VideoCapture(0)

while True:
    _, frame = video.read()
    edge = cv2.Canny(frame, 90, 90)
    cv2.imshow('edge detect', edge)
    exit = cv2.waitKey(1) & 0xff
    if exit == 1:
        break

video.release()
cv2.waitKey(0)
cv2.destroyAllWindows()