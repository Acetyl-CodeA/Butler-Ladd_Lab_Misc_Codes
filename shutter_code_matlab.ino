const int   
// for motor one use 11 13 8 A1
PWM_A   = 11, //3 - 11
DIR_A   = 13, //12 - 13
BRAKE_A = 8, // 9- 8
SNS_A   = A1, //A0 - A1
speed_1 = 255 ,
d_time =200;
byte byteRead;


void setup() {

  // Configure the A output
  pinMode(BRAKE_A, OUTPUT);  // Brake pin on channel A
  pinMode(DIR_A, OUTPUT);    // Direction pin on channel A

  // Open Serial communication
  Serial.begin(9600);
  Serial.println("Motor shield DC motor Test:");
}

void loop() {
  //digitalWrite(BRAKE_A, LOW);  // setting brake LOW disable motor brake
    analogWrite(PWM_A, 0);       // turn off power to the motor
    while (Serial.available()) {
    /* read the most recent byte */
    byteRead = Serial.read();
    

if ( byteRead == 49) {
// Set the outputs to run the motor forward
  Serial.println("forward");

  digitalWrite(DIR_A, HIGH);   // setting direction to HIGH the motor will spin forward

  analogWrite(PWM_A, speed_1);     // Set the speed of the motor, 255 is the maximum value
  
  
  delay(d_time);                 // hold the motor at full speed for  delay miliseconds
// Brake the motor
  // raising the brake pin the motor will stop faster than the stop by inertia
 // digitalWrite(BRAKE_A, HIGH);  // raise the brake

}


if( byteRead == 50) {
// Set the outputs to run the motor backward

  Serial.println("Backward");

  digitalWrite(DIR_A, LOW);    // now change the direction to backward setting LOW the DIR_A pin
  analogWrite(PWM_A, speed_1);     // Set the speed of the motor
  delay(d_time);
//digitalWrite(BRAKE_A, LOW);  // setting againg the brake LOW to disable motor brake
//analogWrite(PWM_A, 0);       // turn off power to the motor
  
}
else {
  // now stop the motor by inertia, the motor will stop slower than with the brake function
  //digitalWrite(BRAKE_A, LOW);  // setting againg the brake LOW to disable motor brake
 analogWrite(PWM_A, 0);       // turn off power to the motor


}


}
}
