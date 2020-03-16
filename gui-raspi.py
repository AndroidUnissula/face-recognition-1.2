import time
from tkinter import filedialog, simpledialog
import cv2
import numpy as np
from tkSimpleStatusbar import *
import os, sys, subprocess
import mysql.connector
import datetime
# untuk di windows
import playsound
from gtts import gTTS


#--------------------------- CONNECT DATABASE ---------------------------#
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="recognizer"
)

master = Tk() # membuat window
master.title("Face Recognition 1.2")
master.resizable(0,0) # me-non aktifkan maximize

#------------------ MEMBUAT STATUS BAR DI MULAI PROGRAM ------------------#
status = StatusBar(master)
status.pack(side=BOTTOM, fill=X)
status.set("selamat datang...")


#------------- MENJALANKAN PATH DAN MEMBUATNYA JIKA TIDAK ADA -------------#
def buatFolder(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

#-------------------- MEMBUAT FUNGSI UNTUK MEMBUKA FILE --------------------#
def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

def detect(): #FUNGSI KETIKA TOMBOL DETECT DI TEKAN
    status.set("identifikasi wajah... tekan q untuk keluar")
    recognizer = cv2.face.LBPHFaceRecognizer_create() # membuat variable untuk menjalanlan algoritma LBPH
    buatFolder("trainer/")
    recognizer.read('trainer/trainer.yml')
    cascadePath = "face-detect.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);
    font = cv2.FONT_HERSHEY_SIMPLEX
    # TODO 3 : Menentukan Kamera yang di pakai
    # cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # Untuk raspberry pi
    cam = cv2.VideoCapture(0)
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # TODO 1 : Menentukan variable viola Jones (scale factor & KNN)
        wajah = faceCascade.detectMultiScale(gray, 1.2, 5)
        kumpulan_nim = []
        kumpulan_waktu = []
        tgl_sekarang = datetime.datetime.date(datetime.datetime.today())

        for (x, y, w, h) in wajah:
            cv2.rectangle(im, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)
            Id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            file_coba = open("biodata.txt", "r")
            semua = file_coba.read()
            pengunjung = eval(semua)
            for pgj in pengunjung:
                if int(pgj[1]) == Id:
                    probalitas = format(round(100 - confidence, 2))
                    # TODO 4 : Menentukan nilai batas minimal / threshold tingkat kemiripan
                    if float(probalitas) > 50.00:
                        Id = (pgj[0] + " " + probalitas)
                        cursor = db.cursor()
                        idd = (pgj[1],)
                        sql3 = "SELECT * FROM pengunjung WHERE id_mhs = %s"
                        cursor.execute(sql3, idd)
                        result = cursor.fetchall()
                        for data in result:
                            if pgj[0] == (data[2]):
                                nm_leng = data[1]
                                nm_pang = data[2]
                                nim = data[3]
                                if data[4] ==1:
                                    status1="Mahasiswa"
                                elif data[4]==2:
                                    status1="Dosen"
                                else:
                                    status1="Pengunjung"
                        sql_select = "SELECT * FROM kedatangan"
                        cursor.execute(sql_select)
                        results = cursor.fetchall()
                        for data in results:
                            kumpulan_waktu.append(str(datetime.datetime.date(data[3])))
                            kumpulan_nim.append(data[2])
                        db.commit()
                        # if nim in kumpulan_nim and str(tgl_sekarang) in kumpulan_waktu:
                        if str(tgl_sekarang) in kumpulan_waktu:
                            pass
                        else:
                            vall = (nm_leng, nim, status1)
                            sqll = "INSERT INTO kedatangan (nama, nim, status) VALUES (%s, %s, %s)"
                            cursor.execute(sqll, vall)
                            db.commit()
                            print("{} data ditambahkan".format(cursor.rowcount))

                            tulisan = ("Selamat datang " + nm_pang)
                            print(tulisan)
                            bahasa = 'id'
                            suara = gTTS(text=tulisan, lang=bahasa, slow=False)
                            suara.save("suara.mp3")
                            # os.system("start output.mp3")

                            # playsound.playsound('suara.mp3', True)
                            os.system("omxplayer -o local suara.mp3")
                    else:
                        Id = "Wajah Tidak dikenal"
                        cv2.rectangle(im, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 0, 255), 4)

            cv2.rectangle(im, (x - 22, y - 90), (x + w + 22, y - 22), (0, 255, 0), -1)
            cv2.putText(im, str(Id), (x, y - 40), font, 1, (255, 255, 255), 3)

        cv2.imshow('Sistem Pengenalan Wajah', im)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
    status.set("Pengenalan wajah siap di jalankan")
def training():
    from PIL import Image
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("face-detect.xml");

    def getImagesAndLabels(path):
        # Ubah path sesuai lokasi penyimpanan gambar untuk raspberry pi
        # path = ("/home/pi/recognizer/dataset")
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []
        mhs = []

        data = 0
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            nama_id = os.path.split(imagePath)[1].split(".")[:2]

            faces = detector.detectMultiScale(img_numpy)
            for (x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y + h, x:x + w])
                ids.append(id)
                data += 1
            jml_gb = 100 / len(imagePaths)
            bb = "Training gambar {0:.0f}%".format(data * jml_gb)
            status.set(bb)

            if nama_id in mhs:
                pass
            else:
                mhs.append(nama_id)

        teks = str(mhs)
        file_bio = open("biodata.txt", "w")
        file_bio.write(teks)
        file_bio.close()

        status.set("Training gambar 100%")
        time.sleep(0.4)
        status.set("Proses Training Selesai")
        return faceSamples, ids

    faces, ids = getImagesAndLabels("dataset")
    recognizer.train(faces, np.array(ids))
    buatFolder('trainer/')
    recognizer.save('trainer/trainer.yml')
    os.system("omxplayer -o local training.mp3")
def new():
    class LoginFrame(Frame):
        def __init__(self, master):
            super().__init__(master)

            self.label_nama_lengkap = Label(self, text="Nama Lenggkap  :")
            self.entry_nama_lengkap = Entry(self)

            self.label_nama_panggilan = Label(self, text="Nama Panggilan :")
            self.entry_nama_panggilan = Entry(self)

            self.label_nim = Label(self, text="NIM/NIK   :")
            self.entry_nim = Entry(self)

            self.label_status = Label(self, text="1=mahasiswa/2=dosen:")
            self.entry_status = Entry(self)

            # Tata Letak
            self.label_nama_lengkap.grid(row=0, sticky=E)
            self.entry_nama_lengkap.grid(row=0, column=1)
            self.label_nama_panggilan.grid(row=1, sticky=E)
            self.entry_nama_panggilan.grid(row=1, column=1)
            self.label_nim.grid(row=2, sticky=E)
            self.entry_nim.grid(row=2, column=1)
            self.label_status.grid(row=3, sticky=E)
            self.entry_status.grid(row=3, column=1)

            self.logbtn = Button(self, text="Kirim Data Baru", command=self.kirimdata)
            self.logbtn.grid(columnspan=2)
            self.pack()

        def kirimdata(self):
            # print("Clicked")
            nama_lengkap = self.entry_nama_lengkap.get()
            nama_penggilan = self.entry_nama_panggilan.get()
            nim = self.entry_nim.get()
            status1 = self.entry_status.get()

            cursor = db.cursor()
            sql = "INSERT INTO pengunjung (nm_lengkap, nm_panggilan,nim,status) VALUES (%s, %s, %s, %s)"
            values = [(nama_lengkap, nama_penggilan, nim, status1)]

            for val in values:
                cursor.execute(sql, val)
                db.commit()

            print("{} data ditambahkan".format(len(values)))
            root.destroy()

            cursor = db.cursor()
            sql2 = "SELECT * FROM pengunjung"
            cursor.execute(sql2)

            result = cursor.fetchall()

            for data in result[-1:]:
                last_id = (data[0])

            # TODO 3 : Menentukan kamera yang akan di pakai
            vid_cam = cv2.VideoCapture(0)
            # Untuk raspberry Pi
            # vid_cam = cv2.VideoCapture(0)
            face_detector = cv2.CascadeClassifier('face-detect.xml')

            face_id = last_id
            face_name = nama_penggilan

            jumlah = 0
            buatFolder("dataset/")
            # TODO 2 : Menentukan Jumlah Gambar Data Training
            jumlah_gambar = 40
            while (True):
                _, image_frame = vid_cam.read()
                gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
                # TODO 1 : Menentukan parameter viola Jones
                wajah = face_detector.detectMultiScale(gray, 1.2, 5)
                for (x, y, w, h) in wajah:
                    cv2.rectangle(image_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    jumlah += 1
                    cv2.imwrite("dataset/" + face_name + "." + str(face_id) + '.' + str(jumlah) + ".jpg",
                                gray[y:y + h, x:x + w])
                    persen_proses = 100 / jumlah_gambar
                    tampil = "Proses pengambilan gambar {0:.0f}%".format(jumlah * persen_proses)
                    status.set(tampil)

                    cv2.imshow('Pengambilan Data Wajah', image_frame)
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                elif jumlah > jumlah_gambar - 1:
                    break
            time.sleep(0.5)
            status.set("Proses pengambilan gambar selesai")
            os.system("omxplayer -o local selesai.mp3")
            # playsound.playsound('selesai.mp3', True)
            vid_cam.release()
            cv2.destroyAllWindows()

    root = Tk()
    root.title("Input data")
    root.resizable(0, 0)  # me-non aktifkan maximize
    lf = LoginFrame(root)
    root.mainloop()
def openfile():
    open_file("dataset")
    os.system("omxplayer -o local hapus.mp3")
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
