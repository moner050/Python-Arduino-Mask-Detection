from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
import numpy as np                                          # numpy 모듈 이름을 np로 지정해 사용
import cv2                                                  # OpenCV

# 얼굴을 찾는 모델
facenet = cv2.dnn.readNet('models/deploy.prototxt', 'models/res10_300x300_ssd_iter_140000.caffemodel')

# 마스크 학습 모델
model = load_model('keras_model_210503.h5')

cap = cv2.VideoCapture('imgs/1234.mp4')                       # 동영상 파일 로드`
# cap = cv2.VideoCapture(2)                                   # 캠 로드
ret, img = cap.read()                                       # 동영상 파일에서 Frame 단위로 읽기

# 동영상 읽기
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
out = cv2.VideoWriter('output.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), (img.shape[1], img.shape[0]))

while cap.isOpened():                                       # 이미지 정보를 실시간으로 받아서 img 에 저장
    ret, img = cap.read()                                   # 동영상 파일에서 Frame 단위로 읽기
    if not ret:                                             # 프레임이 없으면 break 해서 프로그램 종료.
        continue
    h, w = img.shape[:2]                                    # 이미지의 높이와 너비 추출
    # 이미지 전처리
    blob = cv2.dnn.blobFromImage(img, scalefactor=1., size=(300, 300), mean=(104., 177., 123.))
    # facenet 의 input 으로 blob 을 설정
    facenet.setInput(blob)
    # facenet 결과 추론, 얼굴 추출 결과가 dets 에 저장
    dets = facenet.forward()
    # 한 프레임의 내의 여러 얼굴들을 받음.
    result_img = img.copy()
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
        face_input = cv2.resize(face, dsize=(224, 224))
        face_input = cv2.cvtColor(face_input, cv2.COLOR_BGR2RGB)
        face_input = preprocess_input(face_input)
        face_input = np.expand_dims(face_input, axis=0)

        # 마스크 검출 모델로 결과값 return
        Mask_On, Mask_Off, BackGround = model.predict(face_input).squeeze()

        if Mask_On > Mask_Off:
            color = (0, 255, 0)
            label = "Mask On %.2f%%" % (Mask_On * 100)
        else:
            color = (0, 0, 255)
            label = "Mask Off %.2f%%" % (Mask_Off * 100)
        # cv2.rectangle(이미지파일, 시작점 좌표, 종료점 좌표, 선 두께, 색상, 선 종류)
        cv2.rectangle(result_img, pt1=(x1, y1), pt2=(x2, y2), thickness=2, color=color, lineType=cv2.LINE_AA)
        cv2.putText(result_img, text=label, org=(x1, y1 - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, color=color, thickness=2, lineType=cv2.LINE_AA)

    out.write(result_img)
    cv2.imshow('result', result_img)
        # q를 누르면 종료
    if cv2.waitKey(1) == ord('q'):
        break

out.release()
cap.release()

