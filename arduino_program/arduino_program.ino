int led = 2;
int counter = 0;
float Distance1 = 99.59;
float Distance2 = 119.59; //99.59,119.59

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(led, HIGH);
  delay(500);
  digitalWrite(led, LOW);
  delay(500);
  Serial.print(Distance1); Serial.print(","); Serial.println(Distance2);
  // Serial.println("138.58,148.54");
}
