import cv2

windowName = "Live"
cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(windowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cam = cv2.VideoCapture(0)

while True:
    _,img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    cv2.imshow(windowName, img)
    key = cv2.waitKey(30)
    if key == 27:
        break

cam.release()
cv2.destroyAllWindows()