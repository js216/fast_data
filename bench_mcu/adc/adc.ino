// SPDX-License-Identifier: MIT
// adc.ino --- STM32F405 Thing Plus bench helper: ADS9227 comm check.
// Copyright (c) 2026 Jakob Kastelic
//
// Superset of reset.ino: retains the bench reset/identity/pin commands and
// adds a general-purpose ADS9227 configuration-SPI interface so the bench
// MCU can verify communication with the ADC over the intercon FMC link.
//
// The ADS9227 SPI (SCLK/SDI/SDO/CS) is the CONFIGURATION interface only;
// conversion samples leave on a separate LVDS bus to the FPGA and are NOT
// visible here. This sketch can configure the ADC and read back registers
// to prove the link, but it cannot capture samples.

#include <SPI.h>
#include <Wire.h>

// --- ADC control pins (Thing Plus names, from the intercon netlist) ---
#define ADC_SPI_EN   D5   // SPI_EN  : active-HIGH, must be 1 or SDI != SPI data
#define ADC_CS       D9   // CSn     : active-LOW chip select
#define ADC_PWDN_N   A3   // PWDN    : active-LOW power-down (1 = running)
#define ADC_WP_N     A4   // EEPROM_WP (board EEPROM, not the ADC core)
#define ADC_RESET_N  A5   // RESET   : active-LOW (pulse low to reset)

// Config interface: 24-bit frames, MSB-first, SPI mode 0, <=10 MHz.
// Kept slow for bring-up; speed is irrelevant to the readback check.
static const uint32_t ADC_SPI_HZ = 1000000UL;

// --- bench reset / monitored pins (retained from reset.ino) ---
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

static void print_hex(uint32_t v, uint8_t nibbles)
{
  Serial.print("0x");
  for (int i = nibbles - 1; i >= 0; i--) {
    uint8_t nib = (v >> (i * 4)) & 0xF;
    Serial.print((char)(nib < 10 ? '0' + nib : 'A' + nib - 10));
  }
}

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

// --- ADS9227 configuration-SPI primitives ---

// One 24-bit frame; returns the 24-bit value shifted in on SDO. For a read
// frame the register value lands in the low 16 bits (SDO drives after the
// 8-bit address; it is Hi-Z during writes).
static uint32_t adc_xfer24(uint32_t mosi)
{
  SPI.beginTransaction(SPISettings(ADC_SPI_HZ, MSBFIRST, SPI_MODE0));
  digitalWrite(ADC_CS, LOW);
  delayMicroseconds(1);  // CS-falling to first SCLK setup
  uint8_t r0 = SPI.transfer((mosi >> 16) & 0xFF);
  uint8_t r1 = SPI.transfer((mosi >> 8) & 0xFF);
  uint8_t r2 = SPI.transfer(mosi & 0xFF);
  digitalWrite(ADC_CS, HIGH);
  SPI.endTransaction();
  return ((uint32_t)r0 << 16) | ((uint32_t)r1 << 8) | r2;
}

static void adc_write(uint8_t addr, uint16_t data)
{
  adc_xfer24(((uint32_t)addr << 16) | data);
}

// Bank-0 register read; assumes register reads are already enabled.
static uint16_t adc_read(uint8_t addr)
{
  return adc_xfer24((uint32_t)addr << 16) & 0xFFFF;
}

// Enable/read/disable wrapper for a single bank-0 register.
static uint16_t adc_read_reg(uint8_t addr)
{
  adc_write(0x00, 0x0006);  // SPI_RD_EN=1, SPI_MODE=1 (legacy SPI)
  uint16_t v = adc_read(addr);
  adc_write(0x00, 0x0004);  // SPI_RD_EN=0 (resume writes)
  return v;
}

static void adc_set_pins_ready(void)
{
  digitalWrite(ADC_SPI_EN,  HIGH);  // SDI is SPI data
  digitalWrite(ADC_PWDN_N,  HIGH);  // out of power-down
  digitalWrite(ADC_RESET_N, HIGH);  // out of reset
  digitalWrite(ADC_CS,      HIGH);  // deselected
}

static void adc_reset_pulse(void)
{
  digitalWrite(ADC_RESET_N, LOW);
  delay(1);
  digitalWrite(ADC_RESET_N, HIGH);
  delay(1);  // power-up / settle
}

// Conclusive comm check: drive preconditions, reset, then read two distinct
// registers as unique sentinels. Both correct => SCLK+SDI+SDO+CS+SPI_EN+
// PWDN+RESET are all good. Two different expected values guard against a
// stuck/constant SDO reading as a false pass.
static void adc_selftest(void)
{
  adc_set_pins_ready();
  adc_reset_pulse();

  adc_write(0x00, 0x0006);          // enable register reads
  uint16_t v06 = adc_read(0x06);    // REG_00H_READBACK, echoes 0x00 -> 0x0006
  uint16_t v01 = adc_read(0x01);    // DAISY_CHAIN_LEN reset default -> 0x0000
  adc_write(0x00, 0x0004);          // disable reads

  Serial.print("ADC REG06=");
  print_hex(v06, 4);
  Serial.println(" exp=0x0006");
  Serial.print("ADC REG01=");
  print_hex(v01, 4);
  Serial.println(" exp=0x0000");

  bool pass = (v06 == 0x0006) && (v01 == 0x0000);
  Serial.println(pass ? "ADC SELFTEST PASS" : "ADC SELFTEST FAIL");
}

static void i2c_scan(void)
{
  int found = 0;
  for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("I2C ACK ");
      print_hex(addr, 2);
      Serial.println();
      found++;
    }
  }
  Serial.print("I2C done, ");
  Serial.print(found);
  Serial.println(" device(s)");
}

static void print_help(void)
{
  Serial.println("Commands:");
  Serial.println("  r        - pulse D13 low for 100 ms (bench reset A)");
  Serial.println("  R        - pulse D12 low for 100 ms (bench reset B)");
  Serial.println("  ?        - print identity");
  Serial.println("  p        - print monitored pins (D0,D1,D5,D6,D9-D11,A0-A5)");
  Serial.println("  h        - show this help");
  Serial.println("  t        - ADS9227 comm self-test");
  Serial.println("  e N      - set SPI_EN (D5) to 0/1");
  Serial.println("  P N      - set PWDNn (A3) to 0/1 (1=running)");
  Serial.println("  z        - pulse ADC RESETn (A5) low ~1 ms");
  Serial.println("  w HHHHHH - raw 24-bit config frame; prints SDO");
  Serial.println("  g AA     - read ADC bank-0 register AA; prints 16-bit");
  Serial.println("  i        - I2C bus scan");
}

// Dispatch one command. Single-char commands fire immediately the moment the
// byte arrives -- no terminator required -- matching the original reset.ino
// API that test_serv relies on (it sends bare '?','r','R' with no newline).
// Argument-taking commands (w/g/e/P) collect until newline; see loop().
static void run_cmd(char cmd, char *arg)
{
  while (*arg == ' ' || *arg == '\t')
    arg++;

  switch (cmd) {
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
    case 't':
      adc_selftest();
      break;
    case 'e':
      digitalWrite(ADC_SPI_EN, strtoul(arg, NULL, 0) ? HIGH : LOW);
      Serial.print("SPI_EN=");
      Serial.println(digitalRead(ADC_SPI_EN) == HIGH ? "1" : "0");
      break;
    case 'P':
      digitalWrite(ADC_PWDN_N, strtoul(arg, NULL, 0) ? HIGH : LOW);
      Serial.print("PWDNn=");
      Serial.println(digitalRead(ADC_PWDN_N) == HIGH ? "1" : "0");
      break;
    case 'z':
      adc_reset_pulse();
      Serial.println("ADC RESETn pulsed");
      break;
    case 'w': {
      uint32_t v = adc_xfer24(strtoul(arg, NULL, 16) & 0xFFFFFF);
      Serial.print("SDO=");
      print_hex(v, 6);
      Serial.println();
      break;
    }
    case 'g': {
      uint16_t v = adc_read_reg((uint8_t)strtoul(arg, NULL, 16));
      Serial.print("REG=");
      print_hex(v, 4);
      Serial.println();
      break;
    }
    case 'i':
      i2c_scan();
      break;
    default:
      Serial.print("? unknown '");
      Serial.print(cmd);
      Serial.println("'");
      break;
  }
}

void setup(void)
{
  // Bench reset lines to DUT: idle HIGH, active LOW (retained from reset.ino).
  pinMode(D13, OUTPUT);
  digitalWrite(D13, HIGH);
  pinMode(D12, OUTPUT);
  digitalWrite(D12, HIGH);

  // Read-back pins: pull-down so unconnected reads 0 deterministically.
  for (size_t i = 0; i < monitored_n; i++)
    pinMode(monitored[i].pin, INPUT_PULLDOWN);

  // ADC control pins: override the monitored defaults and drive to ready.
  pinMode(ADC_SPI_EN,  OUTPUT);
  pinMode(ADC_CS,      OUTPUT);
  pinMode(ADC_PWDN_N,  OUTPUT);
  pinMode(ADC_RESET_N, OUTPUT);
  pinMode(ADC_WP_N,    OUTPUT);
  digitalWrite(ADC_WP_N, HIGH);  // EEPROM write-protected
  adc_set_pins_ready();

  SPI.begin();
  Wire.begin();

  Serial.begin(115200);
  print_help();
}

static bool cmd_takes_arg(char c)
{
  return c == 'w' || c == 'g' || c == 'e' || c == 'P';
}

void loop(void)
{
  static char arg[32];
  static size_t arglen = 0;
  static char pending = 0;  // arg-taking command awaiting its argument

  while (Serial.available() > 0) {
    char c = Serial.read();

    if (pending) {
      if (c == '\n' || c == '\r') {
        arg[arglen] = 0;
        run_cmd(pending, arg);
        pending = 0;
        arglen = 0;
      } else if (arglen < sizeof(arg) - 1) {
        arg[arglen++] = c;
      }
      continue;
    }

    if (c == '\n' || c == '\r' || c == ' ' || c == '\t')
      continue;  // ignore whitespace between commands

    if (cmd_takes_arg(c)) {
      pending = c;  // begin collecting its argument until newline
      arglen = 0;
    } else {
      run_cmd(c, (char *)"");  // single-char command: act now, no terminator
    }
  }
}
