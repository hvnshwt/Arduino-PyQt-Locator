#define Trig1 6
#define Echo1 7

#define Trig2 4
#define Echo2 5

float Baseline = 100;
float Distance1;
float Distance2;

int TaskTimer1 = 0;
bool TaskFlag1 = false;

void setup() {
  Serial.begin(115200);

  pinMode(Echo1, INPUT);
  pinMode(Echo2, INPUT);
  pinMode(Trig1, OUTPUT);
  pinMode(Trig2, OUTPUT);
  digitalWrite(Trig1, LOW);
  digitalWrite(Trig2, LOW);

  noInterrupts(); 
  TCCR2A = 0;
  TCCR2B = 0;
  TCCR2B |= (1 << CS22) | 
            (1 << CS20) ;
  TCNT2 = 0;
  OCR2A = 125 - 1;
  TIMSK2 |= (1 << OCIE2A);
  interrupts();
}

void loop()
{
  if (TaskFlag1)
  {
    TaskFlag1 = false;
    measure();
    Serial.print(Distance1); Serial.print(","); Serial.println(Distance2);
  }
}

ISR(TIMER2_COMPA_vect)
{
  TaskTimer1++;

  if (TaskTimer1 > 499)
  {
    TaskTimer1 = 0;
    TaskFlag1 = true;
  }
}

void measure()
{
  unsigned long start_time;
  unsigned long finish_time1;
  unsigned long finish_time2;
  unsigned long time_taken;
  boolean echo_flag1;
  boolean echo_flag2;

  digitalWrite(Trig1, HIGH);
  digitalWrite(Trig2, HIGH);
  delayMicroseconds(10);
  digitalWrite(Trig1, LOW);
  digitalWrite(Trig2, LOW);

  while (!digitalRead(Echo1));
  while (!digitalRead(Echo2));

  start_time = micros();

  echo_flag1 = false;
  echo_flag2 = false;

  while ((!echo_flag1) || (!echo_flag2))
  {
    if ((!echo_flag1) && (!digitalRead(Echo1)))
    {
      echo_flag1 = true;
      finish_time1 = micros();
      time_taken = finish_time1 - start_time;
      Distance1 = ((float)time_taken) / 59;
    }

    if ((!echo_flag2) && (!digitalRead(Echo2)))
    {
      echo_flag2 = true;
      finish_time2 = micros();
      time_taken = finish_time2 - start_time;
      Distance2 = ((float)time_taken) / 59;
    }
  }
}