#include <math.h>
const int x_out = A1; /* connect x_out of module to A1 of UNO board */
const int y_out = A2; /* connect y_out of module to A2 of UNO board */
const int z_out = A3; /* connect z_out of module to A3 of UNO board */
const int warning_speed = 20;
const int speed_limit = 50;
const int led= 13;
const float time = 2;
const int trigPin = 9;
const int echoPin = 10;
//int piezoPin = 6;
long duration;
float distance;

double V0 = 0;
float t = 0;

void setup() {
  Serial.begin(9600);
  pinMode(led, OUTPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
  
}
void warning_blink(){
    for(int i = 0; i < 2; i++)
      digitalWrite(led, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(time*250);               // wait for a second
    digitalWrite(led, LOW);    // turn the LED off by making the voltage LOW
    delay(time*250); 
    }
void limit_blink(){
  for(int i = 0; i < 10; i++){
      digitalWrite(led, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(time*50);               // wait for a second
    digitalWrite(led, LOW);    // turn the LED off by making the voltage LOW
    delay(time*50); 
    }
}
void speed(){
  int x_adc_value, y_adc_value, z_adc_value; 
  double x_g_value, y_g_value, z_g_value;
  double roll, pitch, yaw;
  x_adc_value = analogRead(x_out); /* Digital value of voltage on x_out pin */ 
  y_adc_value = analogRead(y_out); /* Digital value of voltage on y_out pin */ 
  z_adc_value = analogRead(z_out); /* Digital value of voltage on z_out pin */ 
  
  x_g_value = ( ( ( (double)(x_adc_value * 5)/1024) - 1.65 ) / 0.330 ); /* Acceleration in x-direction in g units */ 
  y_g_value = ( ( ( (double)(y_adc_value * 5)/1024) - 1.65 ) / 0.330 ); /* Acceleration in y-direction in g units */ 
  z_g_value = ( ( ( (double)(z_adc_value * 5)/1024) - 1.80 ) / 0.330 ); /* Acceleration in z-direction in g units */ 

  double totalAcceleration = sqrt(x_g_value * x_g_value + y_g_value * y_g_value + z_g_value + z_g_value) * 9.81;
  Serial.print("Total acceleration = ");
  Serial.print(totalAcceleration);
  Serial.print("\t");
  
  double velocity = V0 + totalAcceleration * t;
  velocity = velocity / 10;
  t += time;

    
  Serial.print("Speed = ");
  Serial.print(velocity);
  Serial.print("\t");
  if(velocity > warning_speed && velocity < speed_limit){
    warning_blink();    
  }
  else if(velocity> speed_limit){
    limit_blink();      
  } 
  else{
    delay(time*1000);
  }
  Serial.print("\n\n");
  }      

void proximity(){
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
      digitalWrite(6, HIGH);
    //tone(piezoPin, freq, 500);
    }
    if(distance>6)
    {
      digitalWrite(6, LOW);
    }
  }

void loop() {
  speed();
  proximity();
  
}
