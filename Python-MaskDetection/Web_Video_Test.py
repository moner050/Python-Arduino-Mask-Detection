from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
import numpy as np                                 # numpy 모듈 이름을 np로 지정해 사용
import cv2 as cv                                 # cv2 패키지 이름을 cv로 지정해 사용
from urllib.request import urlopen               # 웹캠영상을 불러오기 위한 urlopen 패키지 추가.
import requests                                  # http request를 위한 request 패키지 추가.
from http.client import IncompleteRead           # HTTPException(HTTP관련오류발생처리)의 서브 클래스인 IncompleteRead 패키지추가.
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 얼굴을 찾는 모델
facenet = cv.dnn.readNet('models/deploy.prototxt', 'models/res10_300x300_ssd_iter_140000.caffemodel')
# 학습시킨 모델
model = load_model("keras_model_210503.h5")

url = "http://192.168.???,???/(request 주소)"     # 인터넷에서 영상 불러오기.(ESP32 CAM 설정 후 사용가능)
CAMERA_BUFFER_SIZE = 4316                        # OV2640 카메라의 버퍼 사이즈
streamer = urlopen(url)
bts = b''

oldURL = ''

stream = cv.VideoCapture(streamer)         # 동영상 파일 로드
ret, img = stream.read()                        # 동영상 파일에서 Frame 단위로 읽기
fourcc = cv.VideoWriter_fourcc('m', 'p', '4', 'v')
out = cv.VideoWriter('output.mp4', fourcc, stream.get(cv.CAP_PROP_FPS), (img.shape[1], img.shape[0]))

while stream.isOpened():
    ret, img = stream.read()                    # 동영상 파일에서 Frame 단위로 읽기
    if not ret:                                    # 프레임이 없으면 break 해서 프로그램 종료.
        continue
    try:
        bts += stream.read(CAMERA_BUFFER_SIZE)  # 스트리밍 에러 체크용도
    except IncompleteRead:
        print("ESP32-CAM의 스트리밍 에러가 났습니다.")

    h, w = img.shape[:2]  # 이미지의 높이와 너비 추출
    # 이미지 전처리
    blob = cv.dnn.blobFromImage(img, scalefactor=1., size=(300, 300), mean=(104., 177., 123.))
    # facenet 의 input 으로 blob 을 설정
    facenet.setInput(blob)
    # facenet 결과 추론, 얼굴 추출 결과가 dets 에 저장
    dets = facenet.forward()
    # 한 프레임의 내의 여러 얼굴들을 받음.
    imgg = img.copy()
    # img_won = img.copy()
    # 마스크를 착용했는지 확인
    for i in range(dets.shape[2]):
        # 검출한 결과의 신뢰도
        confidence = dets[0, 0, i, 2]
        # 신뢰도를 0.5로 임계치 설정
        if confidence < 0.5:
            continue

        # 바운딩 박스를 구함
        x1 = int(dets[0, 0, i, 3] * w)
        y1 = int(dets[0, 0, i, 4] * h)
        x2 = int(dets[0, 0, i, 5] * w)
        y2 = int(dets[0, 0, i, 6] * h)

        # 원본 이미지에서 얼굴영역 추출
        face = img[y1:y2, x1:x2]

        # 추출한 얼굴영역을 전처리
        try:
            face_input = cv.resize(face, dsize=(224, 224))              # 배열 팅김현상 try except문으로 해결.
            face_input = cv.cvtColor(face_input, cv.COLOR_BGR2RGB)
            face_input = preprocess_input(face_input)
            face_input = np.expand_dims(face_input, axis=0)
        except cv.error as e:
            print("프레임이 잘못되었습니다")

        # 마스크 검출 모델로 결과값 return
        # 우리꺼 값
        Mask_On, Mask_Off, BackGround = model.predict(face_input).squeeze()

        if Mask_On > Mask_Off:
            color = (0, 255, 0)
            label = "Mask On %.2f%%" % (Mask_On * 100)
            URL = 'http://192.168.?.?/Mask_On'
        elif Mask_On < Mask_Off:
            color = (0, 0, 255)
            label = "Mask Off %.2f%%" % (Mask_Off * 100)
            URL = 'http://192.168.?.?/Mask_Off'
        else :
            color = (255, 0, 0)
            label = "BackGround"
            URL = 'http://192.168.?.?/BackGround'
        if oldURL != URL :
            try:
                response = requests.get(URL)
                print("request send")
            except IncompleteRead:
                print("request send error")

        oldURL = URL

        cv.rectangle(imgg, pt1=(x1, y1), pt2=(x2, y2), thickness=2, color=color, lineType=cv.LINE_AA)
        cv.putText(imgg, text=label, org=(x1, y1 - 10), fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.8, color=color, thickness=2, lineType=cv.LINE_AA)
        out.write(imgg)
        # out.write(imgg)
        cv.imshow('img', imgg)

        # q를 누르면 종료
        if cv.waitKey(1) == ord('q'):
            break
