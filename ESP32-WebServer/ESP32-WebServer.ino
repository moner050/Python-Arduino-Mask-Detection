#include <FS.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <WiFi.h>
#include "soc/soc.h" // brownout was detected 없에기 위한 헤더파일
#include "soc/rtc_cntl_reg.h"  // brownout was detected 없에기 위한 헤더파일

const char* ssid     = "HELLG";
const char* password = "1234qwer!";

// HTTP 로 연결될 포트 설정
AsyncWebServer server(80);

void setup()
{
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // brownout was detected 없에기
    Serial.begin(115200);
    delay(10);
    
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    // 와이파이망에 연결
    while (WiFi.status() != WL_CONNECTED) 
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());  
    
    set_Request();
    startServer();
}

// HTTP Request에 따른 PIN Write설정
void set_Request() 
{    
    // 마스크 꼈다고 인식왔을때
    server.on("/mskon", HTTP_GET, [](AsyncWebServerRequest *request)
    {
        request->send(200, "text/plain", "Mask On Request");
        Serial.println("Mask On Request");
        pinMode(12, OUTPUT);
        pinMode(13, OUTPUT);
        digitalWrite(12, LOW);
        digitalWrite(13, HIGH); 
    });
    
    // 마스크 벗었다고 인식왔을때
    server.on("/mskoff", HTTP_GET, [](AsyncWebServerRequest *request)
    {
        request->send(200, "text/plain", "Mask Off Request");
        Serial.println("Mask Off Request");
        pinMode(12, OUTPUT);
        pinMode(13, OUTPUT);
        digitalWrite(12, HIGH);
        digitalWrite(13, LOW);
    });

    // 사람이 아무도 없다고 인식이 왔을때
    server.on("/background", HTTP_GET, [](AsyncWebServerRequest *request)
    {
        request->send(200, "text/plain", "Background Request");
        Serial.println("Background Request");
        pinMode(12, OUTPUT);
        pinMode(13, OUTPUT);
        digitalWrite(12, LOW);
        digitalWrite(13, LOW);
    });
}


// HTTP 서버 시작
void startServer() {
    server.begin();
}

void loop()
{
    delay(2000);
    set_Request();
}
