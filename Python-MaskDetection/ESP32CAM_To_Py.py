import cv2 as cv                        # cv2 패키지 이름을 cv로 지정해 사용
import numpy as np                      # numpy 모듈 이름을 np로 지정해 사용
from urllib.request import urlopen      # 웹캠영상을 불러오기 위한 urlopen 패키지 추가.

# 서버 주소 입력
url = "http://192.168.1.119:81/stream"
# 카메라 버퍼 사이즈 입력 (OV2640 카메라의 버퍼 사이즈)
CAMERA_BUFFRER_SIZE = 4316
stream = urlopen(url)
bts = b''
i = 0

# 용량문제로 html을 byte화 시킨것을 복호화 시켜야함.
while True:
    try:
        bts += stream.read(CAMERA_BUFFRER_SIZE)                                         # bts에 바이트값 추가.
        jpghead = bts.find(b'\xff\xd8')                                                 # <head></head> 값 찾기
        jpgend = bts.find(b'\xff\xd9')                                                  # <body></body> 값 찾기
        if jpghead > -1 and jpgend > -1:
            jpg = bts[jpghead:jpgend + 2]
            bts = bts[jpgend + 2:]
            img = cv.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv.IMREAD_UNCHANGED)
            img = cv.resize(img, (320, 240))
            cv.imshow("a", img)
        k = cv.waitKey(1)
    except Exception as e:                                                              # 오류가 발생하면 실행시킬 처리
        print("Error:" + str(e))
        bts = b''
        stream = urlopen(url)
        continue

    k = cv.waitKey(1)
    if k & 0xFF == ord('q'):
        break
cv.destroyAllWindows()


