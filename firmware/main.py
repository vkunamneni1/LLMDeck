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

state = {"temp":0.5,"llm":"gpt","status":"Ready","lastResult":""}

def dispSetup():
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

display, textArea = dispSetup()
pixels = neopixel.NeoPixel(board.A3, 3, brightness=0.3, auto_write=False)

def updDisp():
    textArea.text = f"LLM:{state['llm'].upper()} T:{state['temp']:.1f}\n{state['status']}"

def ledBlink(c=(0,255,0)):
    pixels.fill(c)
    pixels.show()
    time.sleep(0.1)
    pixels.fill((0,0,0))
    pixels.show()

def clipGet():
    r = subprocess.run(["xclip","-o","-selection","clipboard"],capture_output=True,text=True,timeout=3)
    return r.stdout.strip() if r.returncode==0 else "No clipboard"

def clipSet(t):
    subprocess.run(["xclip","-selection","clipboard"],input=t,text=True,timeout=3)
    return True

def saveTxt(t):
    with open("/tmp/llmdeck_out.txt","w") as f:
        f.write(t)
    return True

def callGpt(p,c):
    return f"OpenAI response to: {p[:50]}..."

def callGem(p,c):
    return f"Gemini response to: {p[:50]}..."

def callLlam(p,c):
    url="https://ai.hackclub.com/chat/completions"
    headers={"Content-Type":"application/json"}
    body={"messages":[{"role":"user","content":f"{p}\n\n{c}"}]}
    resp=requests.post(url,headers=headers,json=body)
    d=resp.json()
    return d["choices"][0]["message"]["content"]

def doProc(a):
    prompts={
        "summarize":"Summarize this text concisely (without sacrificing clarity) -->",
        "expand":"Expand and elaborate on this text (without sacrificing clarity) -->",
        "humanize":"Rewrite this text to sound more human, real, and natural (without sacrificing clarity) --> "
    }
    state["status"]=f"{a.title()}..."
    updDisp()
    ledBlink((255,255,0))
    content=clipGet()
    prompt=prompts.get(a,"Process this text:")
    if state["llm"]=="gpt":
        result=callGpt(prompt,content)
    elif state["llm"]=="gemini":
        result=callGem(prompt,content)
    elif state["llm"]=="llama":
        result=callLlam(prompt,content)
    else:
        result="No LLM selected"
    state["lastResult"]=result
    saveTxt(result)
    clipSet(result)
    state["status"]="Done!"
    updDisp()
    ledBlink((0,255,0))
    time.sleep(2)
    state["status"]="Ready"
    updDisp()

def swLlm(n):
    state["llm"]=n
    state["status"]=f"→ {n.upper()}"
    updDisp()
    ledBlink((0,0,255))
    time.sleep(1)
    state["status"]="Ready"
    updDisp()

def openBrws(n):
    urls={
        "gpt":"https://chatgpt.com",
        "gemini":"https://gemini.google.com",
        "llama":"https://www.meta.ai"
    }
    state["status"]="Opening..."
    updDisp()
    subprocess.Popen(["xdg-open",urls.get(n,urls["gpt"])])
    state["status"]="Opened"
    ledBlink((255,0,255))
    updDisp()
    time.sleep(1.5)
    state["status"]="Ready"
    updDisp()

def encHand(k,keyboard,*a):
    d=a[0] if a else 0
    t=state["temp"]
    state["temp"]+=d*0.1
    state["temp"]=max(0.0,min(1.0,state["temp"]))
    if t!=state["temp"]:
        updDisp()

def mOpen():
    openBrws(state["llm"])

def mClose():
    state["status"]="Closing"
    updDisp()
    subprocess.run(["pkill","firefox"])
    state["status"]="Closed"
    updDisp()
    time.sleep(1)
    state["status"]="Ready"
    updDisp()

def mSum():
    doProc("summarize")

def mExp():
    doProc("expand")

def mHum():
    doProc("humanize")

def mGpt():
    swLlm("gpt")

def mGem():
    swLlm("gemini")

def mLlam():
    swLlm("llama")

keyboard.keymap=[
    [
        KC.MACRO(mOpen),KC.MACRO(mClose),KC.MACRO(mSum),
        KC.MACRO(mExp),KC.MACRO(mHum),KC.MACRO(mGpt),
        KC.MACRO(mGem),KC.MACRO(mLlam),
    ]
]

keyboard.encoder_handler=encHand

updDisp()
ledBlink()
print("LLMDeck starting...")
keyboard.go()
