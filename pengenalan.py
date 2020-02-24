import datetime
import os
import cv2
import mysql.connector
import mysql.connector
import playsound
from gtts import gTTS

db = mysql.connector.connect(
    host="localhost",
    user="admin",
    passwd="admin123",
    database="recognizer"
)
def buatFolder(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

recognizer = cv2.face.LBPHFaceRecognizer_create()
buatFolder("trainer/")
recognizer.read('trainer/trainer.yml')
cascadePath = "face-detect.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_SIMPLEX
# TODO 3 : Menentukan Kamera yang di pakai
# cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# Untuk raspberry pi
windowName = "Pengujian Pengenalan Wajah"
cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(windowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cam = cv2.VideoCapture(0)
while True:
    ret, im = cam.read()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # TODO 1 : Menentukan variable viola Jones
    wajah = faceCascade.detectMultiScale(gray, 1.2, 5)
    kumpulan_nim = []
    kumpulan_waktu = []
    tgl_sekarang = datetime.datetime.date(datetime.datetime.today())

    for (x, y, w, h) in wajah:
        cv2.rectangle(im, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)
        Id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        file_coba = open("biodata.txt", "r")
        semua = file_coba.read()
        mahasiswa = eval(semua)
        for mhs in mahasiswa:
            if int(mhs[1]) == Id:
                probalitas = format(round(100 - confidence, 2))
                # TODO 4 : Menentukan nilai batas minimal / threshold tingkat kemiripan
                if float(probalitas) > 50.00:
                    Id = (mhs[0] + " " + probalitas)
                    cursor = db.cursor()
                    sql3 = "SELECT * FROM mahasiswa"
                    cursor.execute(sql3)
                    result = cursor.fetchall()
                    for data in result:
                        if mhs[0] == (data[2]):
                            nm_leng = data[1]
                            nm_pang = data[2]
                            nim = data[3]
                    sql_select = "SELECT * FROM kedatangan"
                    cursor.execute(sql_select)
                    results = cursor.fetchall()
                    for data in results:
                        kumpulan_waktu.append(str(datetime.datetime.date(data[3])))
                        kumpulan_nim.append(data[2])
                    db.commit()
                    if nim in kumpulan_nim and str(tgl_sekarang) in kumpulan_waktu:
                        pass
                    else:
                        vall = (nm_leng, nim)
                        sqll = "INSERT INTO kedatangan (nama, nim) VALUES (%s, %s)"
                        cursor.execute(sqll, vall)
                        db.commit()
                        print("{} data ditambahkan".format(cursor.rowcount))

                        tulisan = ("Selamat datang " + nm_pang)
                        print(tulisan)
                        bahasa = 'id'
                        suara = gTTS(text=tulisan, lang=bahasa, slow=False)
                        suara.save("suara.mp3")
                        # os.system("start output.mp3")

                        playsound.playsound('suara.mp3', True)


                else:
                    Id = "Wajah Tidak dikenal"
                    cv2.rectangle(im, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 0, 255), 4)

        cv2.rectangle(im, (x - 22, y - 90), (x + w + 22, y - 22), (0, 255, 0), -1)
        cv2.putText(im, str(Id), (x, y - 40), font, 1, (255, 255, 255), 3)

    cv2.imshow(windowName, im)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
