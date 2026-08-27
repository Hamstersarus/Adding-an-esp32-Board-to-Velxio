/*
 * eeprom-0x78.c - Velxio custom chip: a tiny I2C EEPROM at address 0x78.
 *
 * Deliberately at 0x78 - an address NO standard part uses (24Cxx EEPROMs live
 * at 0x50-0x57). This models a brand-new peripheral added to the simulation.
 *
 * 128 bytes. I2C protocol:
 *   write 1 byte    -> set the address pointer
 *   write 2+ bytes  -> pointer, then sequential data
 *   read            -> byte at pointer, auto-increment
 *
 * Adapted from Velxio's shipped example
 * (frontend/src/components/customChips/examples/eeprom-24c01.c).
 *
 * Build (from a Velxio checkout that has the custom-chip toolchain):
 *   bash scripts/compile-chip.sh path/to/eeprom-0x78.c eeprom-0x78.wasm
 */

#include "velxio-chip.h"
#include <stdlib.h>

#define EEPROM_ADDR 0x78
#define EEPROM_SIZE 128

typedef enum {
  ST_IDLE,        /* before any byte after addressing */
  ST_HAS_POINTER  /* pointer byte received; further writes are data */
} ee_state;

typedef struct {
  uint8_t  pointer;
  uint8_t  mem[EEPROM_SIZE];
  ee_state state;
} chip_state_t;

static bool i2c_connect(void* ud, uint8_t address, bool is_read) {
  chip_state_t* s = (chip_state_t*)ud;
  (void)address;                 /* we only get called for our own address */
  if (!is_read) s->state = ST_IDLE;
  return true;                   /* ACK */
}

static uint8_t i2c_read(void* ud) {
  chip_state_t* s = (chip_state_t*)ud;
  uint8_t b = s->mem[s->pointer & (EEPROM_SIZE - 1)];
  s->pointer = (s->pointer + 1) & (EEPROM_SIZE - 1);
  return b;
}

static bool i2c_write(void* ud, uint8_t byte) {
  chip_state_t* s = (chip_state_t*)ud;
  if (s->state == ST_IDLE) {
    s->pointer = byte & (EEPROM_SIZE - 1);
    s->state = ST_HAS_POINTER;
  } else {
    s->mem[s->pointer & (EEPROM_SIZE - 1)] = byte;
    s->pointer = (s->pointer + 1) & (EEPROM_SIZE - 1);
  }
  return true;                   /* ACK */
}

static void i2c_stop(void* ud) {
  ((chip_state_t*)ud)->state = ST_IDLE;
}

void chip_setup(void) {
  chip_state_t* s = (chip_state_t*)calloc(1, sizeof(chip_state_t));

  vx_i2c_config cfg = {
    .address    = EEPROM_ADDR,   /* fixed 0x78 */
    .scl        = vx_pin_register("SCL", VX_INPUT),
    .sda        = vx_pin_register("SDA", VX_INPUT),
    .on_connect = i2c_connect,
    .on_read    = i2c_read,
    .on_write   = i2c_write,
    .on_stop    = i2c_stop,
    .user_data  = s,
  };
  vx_i2c_attach(&cfg);

  vx_log("EEPROM @ 0x78 ready (custom peripheral, not on the real board)");
}
