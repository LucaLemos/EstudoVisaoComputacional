import cv2
import numpy as np
from time import sleep

video_path = r'videos\Rua.mp4'
delay = 10

cap = cv2.VideoCapture(video_path)
hasFrame, frame = cap.read()

framesIds = cap.get(cv2.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=72)

frames = []
for fid in framesIds:
    cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
    hasFrame, frame = cap.read()
    frames.append(frame)

medianFrame = np.median(frames, axis=0).astype(dtype=np.uint8)

cv2.imwrite('median_frame.jpg', medianFrame)

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
grayMedianFrame = cv2.cvtColor(medianFrame, cv2.COLOR_BGR2GRAY)
cv2.imwrite('median_frame_cinza.jpg', grayMedianFrame)
#cv2.imshow('Cinza', grayMedianFrame)
#cv2.waitKey(0)

while(True):
    tempo = float(1 / delay)
    sleep(tempo)

    hasFrame, frame = cap.read()

    if not hasFrame:
        print("acabou")
        break

    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    dframe = cv2.absdiff(grayFrame, grayMedianFrame)
    th, dframe = cv2.threshold(dframe, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    cv2.imshow('Video Cinza', dframe)
    if cv2.waitKey(1) & 0xFF == ord('c'):
        break

cap.release()


