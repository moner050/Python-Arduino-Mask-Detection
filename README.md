# Python-Arduino-Mask-Detection
Python 마스크 인식 -> ESP32 웹서버 Request -> Arduino 온도측정 및 마스크 착용 유무에대한 음성출력 

사용한 부품 : Arduino Uno, ESP32-CAM, MLX-90614(온도센서), RED LED, GREEN LED, LM386(스피커),LCD 16x2  
사용한 개발 툴 : Pycharm IDE, Arduino IDE

Python을 이용해 동영상 마스크 인식이 잘 되나 테스트 후  
ESP32-CAM에서 카메라 웹 서버 개설 후, 실시간 스트리밍하는 영상을 Python으로 복호화시켜 송출한 다음,  
송출된 영상을 이용해 마스크 인식을 하려고 했으나 응답시간이 너무 느리고 딜레이가 심해서  
핸드폰 카메라를 이용해 영상을 송출받은 뒤 마스크 인식 후 Request를 보내  
ESP32 웹 서버에서 Python에서 받은 Request값에 따라 Pin Write를 설정 후  
Arduino에서 ESP32에서 보낸 핀의 설정에 따라 온도측정 및 음성출력을 하는것을 만들었다.  


1. ESP32-CAM의 카메라 스트리밍 속도가 너무 느리고 Delay가 심함.(CAM 폐기)  
2. 마스크 인식률이 그리 좋지않다. 학습모델을 더 개선시킬 필요 있음. (진행중)  
3. Arduino에 장착한 MLX90614의 온도 측정이 정확하지않다. 온도의 오차를 조정할 필요 있음.(90% 완료)  
4. ESP32에 달린 CAM을 폐기하는 대신 ESP32를 웹 서버로만 이용해서 Request를 보낼예정(완료)  
5. Arduino에 설정한 값이 잘 동작하나 테스트.(테스트 완료)  
6. 테스트용 케이스가 아닌 3D 프린팅한 케이스에 옮긴 후 정상작동 하나 테스트(테스트 완료)  
