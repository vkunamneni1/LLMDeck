# LLMDeck
LLMDeck is an 8 key macropad with a rotary encoder for temperature control, an OLED display, and 3 RGB LEDs for status, all in a 3D-printed 2 part case. 

It runs on a XIAO RP2040 with KMK firmware to prompt multiple LLMs, utilizing them for various everyday tasks.

## Features
- XIAO RP2040 running on KMK firmware
- 3 keys to switch between 3 different LLMs (ChatGPT, Gemini, Llama)
- 3 keys to either summarize, lengthen, or humanize clipboard text
- 2 keys to open corresponding LLM chatbot in browser
- EC11 rotary encoder to adjust prompt temperature (0.0 - 1.0)
- 128×32 0.91" OLED Display (displays current LLM/function)
- 3 RGB LEDs displaying whether LLMDeck is powered on
- 3D-printed case designed in **Onshape**
- Silkscreen of many LLMS and Hack Club!

## Overall CAD Model
![Screenshot 2025-06-29 at 5 18 55 PM](https://github.com/user-attachments/assets/e8ee0596-2062-456e-914a-1f5740d5cf95)

Made in Onshape w/ models from Grabcad

## PCB
### Schematic
![Screenshot 2025-06-29 at 5 19 48 PM](https://github.com/user-attachments/assets/07cf94ea-0e41-4b8e-b212-608a2c0e9c7d)
(also featured on back of PCB!)

### PCB Design
#### With filled zone
![Screenshot 2025-06-29 at 5 21 42 PM](https://github.com/user-attachments/assets/db763846-0fb9-4eb1-a672-e33387d16b1c)

#### Without filled zone
![Screenshot 2025-06-29 at 5 33 28 PM](https://github.com/user-attachments/assets/eecda298-e15c-45b1-aae4-05b680023e78)


### 3D PCB Design
#### Front
![Screenshot 2025-06-29 at 5 22 26 PM](https://github.com/user-attachments/assets/1db2e845-865c-4136-869a-176fd0a7cc49)

#### Back
![Screenshot 2025-06-29 at 5 23 00 PM](https://github.com/user-attachments/assets/8e027afb-63b5-4db4-8728-4b7bc0efe3b1)

## Case
### Top
![Screenshot 2025-06-29 at 5 24 20 PM](https://github.com/user-attachments/assets/ff70c852-4a81-4049-af35-ec529d515d48)

### Bottom
![Screenshot 2025-06-29 at 5 24 45 PM](https://github.com/user-attachments/assets/d9367836-e7fe-4ace-abea-e86517562813)

(complete assembly at top of README)

## Firmware
All firmware was developed in VSCode (w/ KMK). FIRMWARE IS UNTESTED AND WILL PROBABLY NOT WORK. API keys are not included yet (I will add them when I assemble LLMDeck).
- API calls to OpenAI, Google, Meta to utilize LLM functions
- WIFI connection needed
- Data stored in tmp directory
- UNTESTED

## BOM
- 1x Seeed XIAO RP2040
- 9x Through-hole 1N4148 Diodes
- 8x MX-Style switches
- 1x EC11 Rotary encoders
- 1x 0.91 inch OLED display
- 8x Blank DSA keycaps
- 3x SK6812 MINI-E LEDs
- 4x M3x5mx4mm heatset inserts
- 4x M3x16mm screws
- 3D Printed Case (top and bottom)
