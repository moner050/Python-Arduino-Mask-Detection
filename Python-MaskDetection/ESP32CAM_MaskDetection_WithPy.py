import tensorflow as tf
import numpy as np                                 # numpy 모듈 이름을 np로 지정해 사용
import cv2 as cv                                 # cv2 패키지 이름을 cv로 지정해 사용
from urllib.request import urlopen               # 웹캠영상을 불러오기 위한 urlopen 패키지 추가.
import requests                                  # http request를 위한 request 패키지 추가.
from http.client import IncompleteRead           # HTTPException(HTTP관련오류발생처리)의 서브 클래스인 IncompleteRead 패키지추가.
input_size = (224, 224)

# 학습시킨 모델
model = tf.keras.models.load_model("keras_model_210503.h5")

url = "http://192.168.1.119:81/stream"     # 인터넷에서 영상 불러오기.(ESP32 CAM 설정 후 사용가능)
# url = "http://192.168.1.195:81/stream"     # 인터넷에서 영상 불러오기.(ESP32 CAM 설정 후 사용가능)
CAMERA_BUFFRER_SIZE = 4316                        # OV2640 카메라의 버퍼 사이즈
stream = urlopen(url)
bts = b''
oldURL = ''
# 용량문제로 html을 byte화 시킨것을 복호화 시켜야함.
while True:
    try:
        bts += stream.read(CAMERA_BUFFRER_SIZE)                         # bts에 바이트값 추가.
        jpghead = bts.find(b'\xFF\xD8')                                 # <head></head> 값 찾기
        jpgend = bts.find(b'\xFF\xD9')                                  # <body></body> 값 찾기
        # ESP32에서 전송받은 바이트를 복호화해서 영상으로 나타내는 과정.
        if jpghead > -1 and jpgend > -1:
            jpg = bts[jpghead:jpgend + 2]
            bts = bts[jpgend + 2]
            img = cv.imdecode(np.frombuffer(jpg,dtype=np.uint8),cv.IMREAD_UNCHANGED)
            v = cv.flip(img, 0)
            h = cv.flip(img, 1)
            p = cv.flip(img, -1)
            frame = p
            h, w = frame.shape[:2]
            img = cv.resize(frame, (800,600))

            model_frame = cv.resize(frame, input_size, frame)
            model_frame = np.expand_dims(model_frame, axis=0) / 255.0

            is_mask_prob = model.predict(model_frame)[0]
            is_mask = np.argmax(is_mask_prob)

            if is_mask >= 0.5 and is_mask <= 1:
                msg_mask = "Mask Off"
                URL = 'http://192.168.1.119/mskoff'
                # URL = 'http://192.168.1.195/mskoff'
            elif is_mask < 0.5 and is_mask >= 0:
                msg_mask = "Mask On"
                URL = 'http://192.168.1.119/mskon'
                # URL = 'http://192.168.1.195/mskon'
            else:
                msg_mask = "BackGround"
                URL = 'http://192.168.1.119/blank'
                # URL = 'http://192.168.1.195/blank'
            if oldURL != URL :
                try:
                    response = requests.get(URL)
                    print("request send")
                except IncompleteRead:
                    print("request send error")

            oldURL = URL
            msg_mask += "".format(is_mask_prob[is_mask] * 100)
            # 좌측상단 글자 출력 코드(빨간색)
            cv.putText(frame, msg_mask, (10, 70), cv.FONT_HERSHEY_SIMPLEX, 1 , (0, 0, 255), thickness=2)
            cv.imshow('face mask detection', frame)

    except Exception as e:                              #모든 에러문 잡아서 출력.
        print("Error:" + str(e))
        CAMERA_BUFFRER_SIZE = 4316  # OV2640 카메라의 버퍼 사이즈
        bts=b''
        stream=urlopen(url)
        continue

    # q를 누르면 종료

    if cv.waitKey(25) & 0xFF == ord('q'):
        break

