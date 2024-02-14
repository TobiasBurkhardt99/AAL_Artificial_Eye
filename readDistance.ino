#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "Engelburg";
const char* password = "haengtamkuehlschrank";

// MQTT broker
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "UltraschallSensor11101999";
const char* mqtt_topic_level = "UltraschallSensor11101999_level";
const char* mqtt_topic_balance = "UltraschallSensor11101999_balance";

// Define sound speed in cm/uS
#define SOUND_SPEED 0.034

// Define your pins
const int TRIG_PIN_L = 5;
const int ECHO_PIN_L = 18;

const int TRIG_PIN_R = 19;
const int ECHO_PIN_R = 21;

const int TRIG_PIN_M = 23;
const int ECHO_PIN_M = 22;

// Function to read distance from sensor
float readDistance(int trigPin, int echoPin) {
  long duration;
  float distanceCm;

  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance
  distanceCm = duration * SOUND_SPEED / 2;

  return distanceCm;
}

void calculate_level_balance(float data_sensor_left, float data_sensor_mid, float data_sensor_right, int dist_start, int dist_stop, float &level, float &balance) {
    level = 0;
    balance = 0;
    // adjust for level, Peeping starts at distance_start_beeping, Warning at distance_stop 
    int min_dist = min(min(data_sensor_left, data_sensor_mid), data_sensor_right);
    // Serial.print("min_dist: "); Serial.print(min_dist); Serial.print(", dist_start: "); Serial.print(dist_start); Serial.print(", dist_stop: "); Serial.println(dist_stop); // Debugging line
    if (min_dist < dist_stop) {
        level = 1;
    } else if (min_dist < dist_start) {
        level = float(dist_start - min_dist) / dist_start;
    } else {
        level = 0;
    }
    // calculate balance
    if (min_dist < dist_start) {
        // map balance from -1 (most left) to 1 (most right)
        balance = 2 * (float(data_sensor_left) / (data_sensor_left + data_sensor_right)) - 1;
    }
}

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      // Wait 5 seconds before retrying
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN_L, OUTPUT);
  pinMode(ECHO_PIN_L, INPUT);
  pinMode(TRIG_PIN_R, OUTPUT);
  pinMode(ECHO_PIN_R, INPUT);
  pinMode(TRIG_PIN_M, OUTPUT);
  pinMode(ECHO_PIN_M, INPUT);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  } else {
    client.loop();

    // Read distance from sensor
    float distance_L = readDistance(TRIG_PIN_L, ECHO_PIN_L);
    float distance_R = readDistance(TRIG_PIN_R, ECHO_PIN_R);
    float distance_M = readDistance(TRIG_PIN_M, ECHO_PIN_M);

    float level, balance;
    calculate_level_balance(distance_L, distance_M, distance_R, 200, 10, level, balance);

    client.publish(mqtt_topic, String(distance_L).c_str());
    client.publish(mqtt_topic, String(distance_R).c_str());
    client.publish(mqtt_topic, String(distance_M).c_str());
    client.publish(mqtt_topic_level, String(level).c_str());
    client.publish(mqtt_topic_balance, String(balance).c_str());

    delay(500);
  }
}
