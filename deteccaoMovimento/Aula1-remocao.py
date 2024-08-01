import cv2
import numpy as np

video_path = r'videos\Rua.mp4'
#video_path = r'videos\Arco.mp4'
#video_path = r'videos\Estradas.mp4'
#video_path = r'videos\Peixes.mp4'

cap = cv2.VideoCapture(video_path)
hasFrame, frame = cap.read()

framesIds = cap.get(cv2.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=72)

frames = []
for fid in framesIds:
    cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
    hasFrame, frame = cap.read()
    frames.append(frame)

medianFrame = np.median(frames, axis=0).astype(dtype=np.uint8)

cv2.imshow('Median Frame', medianFrame)
cv2.waitKey(0)
cv2.imwrite('median_frame.jpg', medianFrame)




