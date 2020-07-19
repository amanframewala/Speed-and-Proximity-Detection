const int trigPin = 9;
const int echoPin = 10;
int piezoPin = 8;
long duration;
float distance;
void setup() {
  // put your setup code here, to run once:
pinMode(trigPin, OUTPUT);
pinMode(echoPin, INPUT);
Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
digitalWrite(trigPin,LOW);
delayMicroseconds(1000);
digitalWrite(trigPin, HIGH);
delayMicroseconds(10);
digitalWrite(trigPin, LOW);
duration = pulseIn(echoPin, HIGH);
distance = duration*0.034/2;
Serial.print("Distance:");
Serial.println(distance);
int freq = 1000;
float lastval = distance;
float currval;
float delta = currval-lastval;
lastval = currval;
freq += delta * 1000;
if(distance<6)
{
tone(piezoPin, freq, 500);
}
}
