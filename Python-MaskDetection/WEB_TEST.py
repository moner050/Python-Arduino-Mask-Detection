from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
import numpy as np                                 # numpy 모듈 이름을 np로 지정해 사용
import cv2 as cv                                 # cv2 패키지 이름을 cv로 지정해 사용
from urllib.request import urlopen               # 웹캠영상을 불러오기 위한 urlopen 패키지 추가.
import requests                                  # http request를 위한 request 패키지 추가.
from http.client import IncompleteRead           # HTTPException(HTTP관련오류발생처리)의 서브 클래스인 IncompleteRead 패키지추가.

input_size = (224, 224)

# 얼굴을 찾는 모델
facenet = cv.dnn.readNet('models/deploy.prototxt', 'models/res10_300x300_ssd_iter_140000.caffemodel')
# 학습시킨 모델
model = load_model("keras_model_210503.h5", compile=False)

url = "http://192.168.1.119:81/stream"     # 인터넷에서 영상 불러오기.(ESP32 CAM 설정 후 사용가능)
CAMERA_BUFFER_SIZE = 4316                        # OV2640 카메라의 버퍼 사이즈
stream = urlopen(url)
bts = b''
oldURL = ''

while True:
    try:
        bts += stream.read(CAMERA_BUFFER_SIZE)  # 스트리밍 에러 체크
    except IncompleteRead:
        print("ESP32-CAM의 스트리밍 에러가 났습니다.")

    # ESP32에서 전송받은 바이트를 복호화해서 영상으로 나타내는 과정.
    jpghead = bts.find(b'\xff\xd8')
    jpgend = bts.find(b'\xff\xd9')

    if jpghead > -1 and jpgend > -1:
        jpg = bts[jpghead:jpgend + 2]
        bts = bts[jpgend + 2]
        img = cv.imencode(np.frombuffer(jpg, dtype=np.uint8), cv.IMREAD_UNCHANGED)
        v = cv.flip(img, 0)
        h = cv.flip(img, 1)
        p = cv.flip(img, -1)
        frame = p

        h, w = frame.shape[:2]
        img = cv.resize(frame, (800,600))

        model_frame = cv.resize(frame, input_size, frame)

        model_frame = np.expand_dims(model_frame, axis=0) / 255.0

        What_Mask = model.predict(model_frame)[0]
        What_Msk = np.argmax(What_Mask)

        if What_Msk == 1:
            color = (0, 0, 255)
            msg_mask = "Mask Off"
            URL = 'http://192.168.1.119/Mask_Off'
        elif What_Msk == 0:
            color = (0, 255, 0)
            msg_mask = "Mask On"
            URL = 'http://192.168.1.119/Mask_ON'
        else:
            color = (255, 0, 0)
            msg_mask = "BackGround"
            URL = 'http://192.168.1.119/BackGround'
        if oldURL != URL :
            try:
                response = requests.get(URL)
                print("request send")
            except IncompleteRead:
                print("request send error")

        oldURL = URL

         # Show the result and frame
        cv.imshow('face mask detection', frame)

         # Press Q on keyboard to  exit
        if cv.waitKey(25) & 0xFF == ord('q'):
            break