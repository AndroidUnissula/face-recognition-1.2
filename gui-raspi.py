import os
import time
from tkinter import filedialog, simpledialog
import cv2
import numpy as np

from tkSimpleStatusbar import *

master = Tk() # membuat window
master.title("Face Recognition 1.2")
master.resizable(0,0) # me-non aktifkan maximize

#------------------ MEMBUAT STATUS BAR DI MULAI PROGRAM ------------------#
status = StatusBar(master)
status.pack(side=BOTTOM, fill=X)
status.set("selamat datang...")
def buatFolder(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

def detect():
    status.set("identifikasi wajah... tekan q untuk keluar")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    buatFolder("trainer/")
    recognizer.read('trainer/trainer.yml')
    cascadePath = "face-detect.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);
    font = cv2.FONT_HERSHEY_SIMPLEX
    # cam = cv2.VideoCapture(0)
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        wajah = faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in wajah:
            cv2.rectangle(im, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)
            Id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            file_coba = open("data_mahasiswa.txt", "r")
            semua = file_coba.read()
            mahasiswa = semua.split('''\n''')
            data_mhs = []
            for siswa in mahasiswa:
                data_mhs.append(siswa.split("."))
            for mhs in data_mhs:
                if int(mhs[0]) == Id:
                    Id = (mhs[1]) + " {0:.2f}%".format(round(100 - confidence, 2))

            cv2.rectangle(im, (x - 22, y - 90), (x + w + 22, y - 22), (0, 255, 0), -1)
            cv2.putText(im, str(Id), (x, y - 40), font, 1, (255, 255, 255), 3)
        cv2.imshow('Pengujian Pengenalan Wajah', im)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
    status.set("Pengenalan wajah siap di jalankan")


def training():
    from PIL import Image
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("face-detect.xml");
    def getImagesAndLabels():
        path = ("/home/pi/recognizer/dataset")
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []
        data = 0
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_numpy)
            for (x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y + h, x:x + w])
                ids.append(id)
                data += 1
            jml_gb = 100 / len(imagePaths)
            bb = "Training gambar {0:.0f}%".format(data * jml_gb)
            status.set(bb)
            # sys.stdout.write('\r' + bb)
            # time.sleep(0.0000001)
        # sys.stdout.write('\r' + "Training gambar 100%")
        status.set("Training gambar 100%")
        time.sleep(0.4)
        status.set("Proses Training Selesai")
        return faceSamples, ids
    faces, ids= getImagesAndLabels()
    recognizer.train(faces, np.array(ids))
    buatFolder('trainer/')
    recognizer.save('trainer/trainer.yml')
def new():
    vid_cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    face_detector = cv2.CascadeClassifier('face-detect.xml')
    face_id = simpledialog.askstring(title="Pelabelan Wajah", prompt="Masukkan Id :")
    face_name = simpledialog.askstring(title="Pelabelan Wajah", prompt="Masukkan nama :")

    text = "\n" + face_id+"."+face_name
    file_bio = open("data_mahasiswa.txt", "a")
    file_bio.write(text)
    file_bio.close()

    jumlah = 0
    buatFolder("dataset/")
    jumlah_gambar = 40
    while (True):
        _, image_frame = vid_cam.read()
        gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
        wajah = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in wajah:
            cv2.rectangle(image_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            jumlah += 1
            cv2.imwrite("dataset/"+face_name+"." + str(face_id) + '.' + str(jumlah) + ".jpg", gray[y:y + h, x:x + w])
            persen_proses = 100 / jumlah_gambar
            tampil = "Proses pengambilan gambar {0:.0f}%".format(jumlah * persen_proses)
            status.set(tampil)
            # sys.stdout.write('\r' + str(tampil))
            # time.sleep(0.0000000001)
            cv2.imshow('Pengambilan Data Wajah', image_frame)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
        elif jumlah > jumlah_gambar - 1:
            break
    time.sleep(0.5)
    status.set("Proses pengambilan gambar selesai")
    vid_cam.release()
    cv2.destroyAllWindows()
def openfile():
    master.filename = filedialog.askopenfilenames(initialdir="dataset/", title="Hapus file yang bukan wajah",filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))

#----------------------- MEMBUAT TOMBOL GAMBAR -----------------------#
img_detect = PhotoImage(file="img/face_detec.png").subsample(15,15)
img_new = PhotoImage(file="img/add_data.png").subsample(15,15)
img_train = PhotoImage(file="img/training.png").subsample(15,15)
img_openfile = PhotoImage(file="img/files.png").subsample(15,15)

btn_detect = Button(master,image = img_detect,compound=LEFT,command=detect, text="Detect").pack(side=LEFT)
btn_new = Button(master,image=img_new,compound=LEFT,command=new,text="New").pack(side=LEFT)
btn_train = Button(master,image=img_train,compound=LEFT,command=training,text="Training").pack(side=LEFT)
btn_openfile = Button(master,image=img_openfile,compound=LEFT,command=openfile,text="Open file").pack(side=LEFT)

master.mainloop() # penutup window agar tidak langsung keluar
master.quit() # keluar  dari window