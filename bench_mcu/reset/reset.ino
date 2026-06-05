// SPDX-License-Identifier: MIT
// reset.ino --- STM32F405 Thing Plus bench helper.
// Copyright (c) 2026 Jakob Kastelic

static const struct {
  int         pin;
  const char *name;
} monitored[] = {
  {D0,  "D0" }, {D1,  "D1" },
  {D5,  "D5" }, {D6,  "D6" },
  {D9,  "D9" }, {D10, "D10"}, {D11, "D11"},
  {A0,  "A0" }, {A1,  "A1" }, {A2,  "A2" }, {A3,  "A3" },
  {A4,  "A4" }, {A5,  "A5" },
};

static const size_t monitored_n = sizeof(monitored) / sizeof(monitored[0]);

static void print_pins(void)
{
  for (size_t i = 0; i < monitored_n; i++) {
    Serial.print(monitored[i].name);
    Serial.print("=");
    Serial.print(digitalRead(monitored[i].pin) == HIGH ? "1" : "0");
    if (i < monitored_n - 1)
      Serial.print(" ");
  }
  Serial.println();
}

static void print_help(void)
{
  Serial.println("Commands:");
  Serial.println("  r  - pulse D13 low for 100 ms");
  Serial.println("  R  - pulse D12 low for 100 ms");
  Serial.println("  ?  - print identity");
  Serial.println("  p  - print monitored pins (D0,D1,D5,D6,D9-D11,A0-A5)");
  Serial.println("  h  - show this help");
}

void setup(void)
{
  // Reset line to DUT: idle HIGH, active LOW.
  pinMode(D13, OUTPUT);
  digitalWrite(D13, HIGH);
  pinMode(D12, OUTPUT);
  digitalWrite(D12, HIGH);

  // All read-back pins: pull-down so unconnected reads 0 deterministically.
  for (size_t i = 0; i < monitored_n; i++)
    pinMode(monitored[i].pin, INPUT_PULLDOWN);

  Serial.begin(115200);
  print_help();
}

void loop(void)
{
  if (Serial.available() <= 0)
    return;

  char c = Serial.read();

  switch (c) {
    case 'r':
      digitalWrite(D13, LOW);
      delay(100);
      digitalWrite(D13, HIGH);
      break;
    case 'R':
      digitalWrite(D12, LOW);
      delay(100);
      digitalWrite(D12, HIGH);
      break;
    case '?':
      Serial.println("STM32F405");
      break;
    case 'p':
      print_pins();
      break;
    case 'h':
      print_help();
      break;
    case '\r':
    case '\n':
    case ' ':
      break;  // ignore whitespace
    default:
      Serial.print("? unknown '");
      Serial.print(c);
      Serial.println("'");
      break;
  }
}
