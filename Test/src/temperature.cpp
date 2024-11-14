#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Arduino.h>
#include "DHTesp.h"
#include <ESP32Servo.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define DHTPIN 17
#define DHTTYPE DHT11
#define btn1 16
#define btn2 27
#define fanPin1 19
#define fanPin2 18
#define led_y 12
#define buzzer_pin 25

LiquidCrystal_I2C mylcd(0x27, 16, 2);
DHTesp dht;

const char *ssid = "iPhone de Noe";
const char *password = "noephone";

void setup()
{
  Serial.begin(115200);
  mylcd.init();
  mylcd.backlight();
  pinMode(fanPin1, OUTPUT);
  pinMode(fanPin2, OUTPUT);
  pinMode(btn1, INPUT);
  pinMode(btn2, INPUT);
  pinMode(led_y, OUTPUT);
  pinMode(buzzer_pin, OUTPUT);
  dht.setup(17, DHTesp::DHT11);

  // Connexion Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connexion au Wi-Fi");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connecté au Wi-Fi");
}

void loop()
{
  delay(dht.getMinimumSamplingPeriod());

  float humidity = dht.getHumidity();
  float temperature = dht.getTemperature();

  mylcd.setCursor(0, 0);
  mylcd.print("T = ");
  mylcd.print(temperature);
  mylcd.print(" C ");
  mylcd.setCursor(0, 1);
  mylcd.print("H = ");
  mylcd.print(humidity);
  mylcd.print(" % ");

  if (temperature > 25)
  {
    digitalWrite(led_y, HIGH);
  }
  else
  {
    digitalWrite(led_y, LOW);
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    HTTPClient http;
    http.begin("http://172.20.10.3:5000/data"); // Remplacez par l'adresse IP et le port de votre serveur
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"temperature\":" + String(temperature) + ",\"humidity\":" + String(humidity) + "}";

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0)
    {
      String response = http.getString();
      Serial.println("Réponse du serveur: " + response);
    }
    else
    {
      Serial.println("Erreur dans la requête POST: " + String(httpResponseCode));
    }

    http.end();
  }
  else
  {
    Serial.println("Non connecté au Wi-Fi");
  }

  delay(2000);
}
