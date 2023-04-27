'''Downlaod all the neccesary libraries
        change the adrress for the py tesseracts according to the system '''

from tkinter import *
import cv2 as cv
import time
import datetime
from PIL import ImageTk, Image
import pytesseract
import playsound
import mysql.connector

mydb = mysql.connector.connect(host="localhost",
                               username='root',
                               password='root',# Change the database username and password
                               database='OCR')

# if mydb.is_connected():
# print("Connection is secured")

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
Indian_LP = cv.CascadeClassifier("Haar_cascade.xml")


class App:
    def __init__(self, video_source=0):
        self.appName = "ALNPR"
        self.Window = Tk()
        self.Window.title(self.appName)
        self.Window.resizable(True, True)
        self.Window['bg'] = 'black'
        self.video_source = video_source
        self.vid = VideoCapture(self.video_source)
        self.label = Label(self.Window, text=self.appName, font=15,
                           bg='blue', fg='white').pack(side=TOP, fill=BOTH)
        # canvas
        self.canvas1 = Canvas(self.Window, bg='White', highlightthickness=0, width=600, height=400)
        self.canvas1.pack()

        # Button that starts the ALNPR scanning

        self.update()
        self.Window.mainloop()

    def update(self):
        isTrue, frame = self.vid.getFrame()
        frame = cv.flip(frame, 1)

        if isTrue:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas1.create_image(0, 0, image=self.photo, anchor=NW)
        self.Window.after(1, self.update)


class VideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to find the open the video source")

        # Get video width and height
        self.width = self.vid.set(cv.CAP_PROP_FRAME_WIDTH, 800)
        self.height = self.vid.set(cv.CAP_PROP_FRAME_HEIGHT, 600)

    def getFrame(self):

        cur = mydb.cursor()
        global new_img
        if self.vid.isOpened():
            isTrue, frame = self.vid.read()
            if isTrue:
                # return the frame
                gray_img = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                Noise_reduc = cv.bilateralFilter(gray_img, 11, 17, 17)
                lp_detect = Indian_LP.detectMultiScale(Noise_reduc, scaleFactor=2.5, minNeighbors=10)
                for (x, y, w, h) in lp_detect:
                    frs = frame[y:y + h, x:x + w]
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), thickness=1)
                    new_img = frame[y:y + h, x:x + w]
                    cv.imshow("Plate", new_img)
                if cv.waitKey(1) & 0xFF == ord('s'):
                    cv.imwrite('demofile.png', new_img)
                    playsound.playsound(r"C:\Users\ROHIT\PycharmProjects\pythonProject\OpenCV\Beep1.wav")

                    Cropped_loc = r'C:\Users\ROHIT\PycharmProjects\pythonProject\College_Project\demofile.png'
                    plate = pytesseract.image_to_string(Cropped_loc, lang='eng',
                                                        config='--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                    print(plate)
                    sql = "INSERT INTO Number_Plate(Number,State,Plate_Image) VALUES (%s, %s, %s)"
                    val = (plate, plate[:2], 'demofile.png')
                    cur.execute(sql, val)
                    mydb.commit()
                    database()

                return (isTrue, cv.cvtColor(frame, cv.COLOR_BGR2RGB))
            else:
                return (isTrue, None)
        else:
            return (isTrue, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


class database:
    def __init__(self):
        self.cursor = None
        self.Appname = 'Database'
        self.Win = Tk()
        self.Win.title(self.Appname)
        self.Win['bg'] = 'black'
        self.Win['bg'] = 'black'
        self.canvas = Canvas(self.Win, bg='White', highlightthickness=0, width=600, height=400)
        self.canvas.pack()
        self.database_loop()
        self.Win.mainloop(100)

    def database_loop(self):
        self.cursor = mydb.cursor()
        self.cursor.execute("select * from Number_Plate order by data_record_time desc LIMIT 5;")
        i = 1
        e = Label(self.canvas, width=15, text="Plate Number", borderwidth=1, relief='ridge', anchor='w',
                  bg='Yellow')
        e.grid(row=0, column=0)
        e = Label(self.canvas, width=15, text="State", borderwidth=1, relief='ridge', anchor='w', bg='Yellow')
        e.grid(row=0, column=1)
        e = Label(self.canvas, width=15, text="Image Address", borderwidth=1, relief='ridge', anchor='w',
                  bg='Yellow')
        e.grid(row=0, column=2)
        e = Label(self.canvas, width=15, text="TimeStamp", borderwidth=1, relief='ridge', anchor='w', bg='Yellow')
        e.grid(row=0, column=3)
        for entry in self.cursor:
            for j in range(len(entry)):
                e = Label(self.canvas, width=15, text=entry[j], borderwidth=1, relief='ridge', anchor='w')
                e.grid(row=i, column=j)

            i += 1

        mydb.commit()


if __name__ == "__main__":
    App()
