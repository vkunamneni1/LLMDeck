import board
import time
import subprocess
import digitalio
import storage
import supervisor
from pathlib import Path
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.matrix import DiodeOrientation
from kmk.handlers.sequences import send_string
from kmk.extensions.display import Display, TextEntry, ImageEntry
from kmk.extensions.RGB import RGB, AnimationModes
from kmk.modules.encoder import EncoderHandler
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306
import neopixel
from adafruit_requests import requests
import adafruit_connection_manager
import ssl
import socketpool
import wifi

keyboard = KMKKeyboard()

keyboard.col_pins = (board.A0, board.A1, board.A2)
keyboard.row_pins = (board.D3, board.D2, board.D1)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

encoder = EncoderHandler()
encoder.pins = ((board.RX, board.TX, board.D0, False),)
keyboard.modules.append(encoder)

state = {
    "temp": 0.5,
    "llm": "gpt",
    "status": "Ready",
    "lastResult": ""
}

def setupDisplay():
    displayio.release_displays()
    i2c = board.I2C()
    bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    oled = SSD1306(bus, width=128, height=32)

    splash = displayio.Group()
    oled.show(splash)

    text = label.Label(
        terminalio.FONT,
        text="LLM Deck v1.0",
        color=0xFFFFFF,
        x=2, y=8
    )
    splash.append(text)

    return oled, text

display, textArea = setupDisplay()

pixels = neopixel.NeoPixel(board.A3, 3, brightness=0.3, auto_write=False)

def updateDisplay():
    textArea.text = (
        f"LLM:{state['llm'].upper()} T:{state['temp']:.1f}\n{state['status']}"
    )

def flashLeds(color=(0, 255, 0)):
    pixels.fill(color)
    pixels.show()
    time.sleep(0.1)
    pixels.fill((0, 0, 0))
    pixels.show()

def getClipboard():
    result = subprocess.run(
        ["xclip", "-o", "-selection", "clipboard"],
        capture_output=True, text=True, timeout=3
    )
    return result.stdout.strip() if result.returncode == 0 else "No clipboard"

def setClipboard(text):
    subprocess.run(
        ["xclip", "-selection", "clipboard"],
        input=text, text=True, timeout=3
    )
    return True

def saveResult(text):
    with open("/tmp/llmdeck_out.txt", "w") as f:
        f.write(text)
    return True

def callOpenai(prompt, content):
    return f"OpenAI response to: {prompt[:50]}..."

def callGemini(prompt, content):
    return f"Gemini response to: {prompt[:50]}..."

def callLlama(prompt, content):
    url = "https://ai.hackclub.com/chat/completions"
    headers = {"Content-Type": "application/json"}
    body = {
        "messages": [
            {"role": "user", "content": f"{prompt}\n\n{content}"}
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    return data["choices"][0]["message"]["content"]

def processText(action):
    prompts = {
        "summarize": "Summarize this text concisely (without sacrificing clarity) -->",
        "expand": "Expand and elaborate on this text (without sacrificing clarity) -->",
        "humanize": "Rewrite this text to sound more human, real, and natural (without sacrificing clarity) --> "
    }

    state["status"] = f"{action.title()}..."
    updateDisplay()
    flashLeds((255, 255, 0))

    content = getClipboard()
    prompt = prompts.get(action, "Process this text:")

    if state["llm"] == "gpt":
        result = callOpenai(prompt, content)
    elif state["llm"] == "gemini":
        result = callGemini(prompt, content)
    elif state["llm"] == "llama":
        result = callLlama(prompt, content)
    else:
        result = "No LLM selected"

    state["lastResult"] = result
    saveResult(result)
    setClipboard(result)

    state["status"] = "Done!"
    updateDisplay()
    flashLeds((0, 255, 0))

    time.sleep(2)
    state["status"] = "Ready"
    updateDisplay()

def switchLlm(name):
    state["llm"] = name
    state["status"] = f"→ {name.upper()}"
    updateDisplay()
    flashLeds((0, 0, 255))
    time.sleep(1)
    state["status"] = "Ready"
    updateDisplay()

def openBrowser(name):
    urls = {
        "gpt": "https://chatgpt.com",
        "gemini": "https://gemini.google.com",
        "llama": "https://www.meta.ai"
    }

    state["status"] = "Opening..."
    updateDisplay()

    subprocess.Popen(["xdg-open", urls.get(name, urls["gpt"])])
    state["status"] = "Opened"
    flashLeds((255, 0, 255))

    updateDisplay()
    time.sleep(1.5)
    state["status"] = "Ready"
    updateDisplay()

def encoderHandler(key, keyboard, *args):
    direction = args[0] if args else 0
    oldTemp = state["temp"]
    state["temp"] += direction * 0.1
    state["temp"] = max(0.0, min(1.0, state["temp"]))
    if oldTemp != state["temp"]:
        updateDisplay()

def macroOpenChat():
    openBrowser(state["llm"])

def macroCloseChat():
    state["status"] = "Closing"
    updateDisplay()
    subprocess.run(["pkill", "firefox"])
    state["status"] = "Closed"
    updateDisplay()
    time.sleep(1)
    state["status"] = "Ready"
    updateDisplay()

def macroSummarize():
    processText("summarize")

def macroExpand():
    processText("expand")

def macroHumanize():
    processText("humanize")

def macroGpt():
    switchLlm("gpt")

def macroGemini():
    switchLlm("gemini")

def macroLlama():
    switchLlm("llama")

keyboard.keymap = [
    [
        KC.MACRO(macroOpenChat), KC.MACRO(macroCloseChat), KC.MACRO(macroSummarize),
        KC.MACRO(macroExpand), KC.MACRO(macroHumanize), KC.MACRO(macroGpt),
        KC.MACRO(macroGemini), KC.MACRO(macroLlama), KC.NO,
    ]
]

keyboard.encoder_handler = encoderHandler

updateDisplay()
flashLeds()

if __name__ == "__main__":
    print("LLMDeck starting...")
    keyboard.go()
