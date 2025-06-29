# imports -->

import board
import time
import subprocess
import digitalio
import storage
import supervisor
import ssl
import socketpool
import wifi
import neopixel
import displayio
import terminalio
from pathlib import Path
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.matrix import DiodeOrientation
from kmk.handlers.sequences import send_string
from kmk.extensions.display import Display, TextEntry, ImageEntry
from kmk.extensions.RGB import RGB, AnimationModes
from kmk.modules.encoder import EncoderHandler
from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306
from adafruit_requests import requests

# setup -->

keyboard = KMKKeyboard()
keyboard.col_pins = (board.A0, board.A1, board.A2)
keyboard.row_pins = (board.D3, board.D2, board.D1)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

encoder = EncoderHandler()
encoder.pins = ((board.RX, board.TX, board.D0, False),)
keyboard.modules.append(encoder)

state = {"temp":0.5,"llm":"gpt","status":"Ready","lastResult":""}

# functions starting from here-->

def setupDisp():
    displayio.release_displays()
    i2c = board.I2C()
    bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    oled = SSD1306(bus, width=128, height=32)
    splash = displayio.Group()
    oled.show(splash)
    text = label.Label(
        terminalio.FONT,
        text="LLMDeck",
        color=0xFFFFFF,
        x=2, y=8
    )
    splash.append(text)
    return oled, text

display, textArea = setupDisp()
pixels = neopixel.NeoPixel(board.A3, 3, brightness=0.3, auto_write=False)

def refreshDisp():
    textArea.text = f"LLM:{state['llm'].upper()} T:{state['temp']:.1f}\n{state['status']}"

def blinkLeds(c=(0,255,0)):
    pixels.fill(c)
    pixels.show()
    time.sleep(0.1)
    pixels.fill((0,0,0))
    pixels.show()

def grabClipboard():
    r = subprocess.run(["xclip","-o","-selection","clipboard"],capture_output=True,text=True,timeout=3)
    return r.stdout.strip() if r.returncode==0 else "No clipboard"

def setClipboard(t):
    subprocess.run(["xclip","-selection","clipboard"],input=t,text=True,timeout=3)
    return True

def writeResult(t):
    with open("/tmp/llmdeck_out.txt","w") as f:
        f.write(t)
    return True

def fetchOpenai(p,c):
    return f"OpenAI response to: {p[:50]}"

def fetchGemini(p,c):
    return f"Gemini response to: {p[:50]}"

def fetchLlama(p,c):
    url="https://ai.hackclub.com/chat/completions"
    headers={"Content-Type":"application/json"}
    body={"messages":[{"role":"user","content":f"{p}\n\n{c}"}]}
    resp=requests.post(url,headers=headers,json=body)
    d=resp.json()
    return d["choices"][0]["message"]["content"]

def handleAction(a):
    prompts={
        "summarize":"Summarize this text concisely (without sacrificing clarity) -->",
        "expand":"Expand and elaborate on this text (without sacrificing clarity) -->",
        "humanize":"Rewrite this text to sound more human, real, and natural (without sacrificing clarity) --> "
    }
    state["status"]=f"{a.title()}"
    refreshDisp()
    blinkLeds((255,255,0))
    content=grabClipboard()
    prompt=prompts.get(a,"Process this text:")
    if state["llm"]=="gpt":
        result=fetchOpenai(prompt,content)
    elif state["llm"]=="gemini":
        result=fetchGemini(prompt,content)
    elif state["llm"]=="llama":
        result=fetchLlama(prompt,content)
    else:
        result="No LLM selected"
    state["lastResult"]=result
    writeResult(result)
    setClipboard(result)
    state["status"]="Done!"
    refreshDisp()
    blinkLeds((0,255,0))
    time.sleep(2)
    state["status"]="Ready"
    refreshDisp()
def changeLlm(n):
    state["llm"]=n
    state["status"]=f"→ {n.upper()}"
    refreshDisp()
    blinkLeds((0,0,255))
    time.sleep(1)
    state["status"]="Ready"
    refreshDisp()

def launchBrowser(n):
    urls={
        "gpt":"https://chatgpt.com",
        "gemini":"https://gemini.google.com",
        "llama":"https://www.meta.ai"
    }
    state["status"]="Opening..."
    refreshDisp()
    subprocess.Popen(["xdg-open",urls.get(n,urls["gpt"])])
    state["status"]="Opened"
    blinkLeds((255,0,255))
    refreshDisp()
    time.sleep(1.5)
    state["status"]="Ready"
    refreshDisp()

def handleEncoder(k,keyboard,*a):
    d=a[0] if a else 0
    t=state["temp"]
    state["temp"]+=d*0.1
    
    state["temp"]=max(0.0,min(1.0,state["temp"]))
    if t!=state["temp"]:
        refreshDisp()

def macroOpen():
    launchBrowser(state["llm"])

def macroClose():
    state["status"]="Closing"
    refreshDisp()
    subprocess.run(["pkill","firefox"])
    state["status"]="Closed"
    refreshDisp()
    time.sleep(1)
    state["status"]="Ready"
    refreshDisp()

def macroSummarize():
    handleAction("summarize")

def macroExpand():
    handleAction("expand")

def macroHumanize():
    handleAction("humanize")


def macroGpt():
    changeLlm("gpt")

def macroGemini():
    changeLlm("gemini")

def macroLlama():
    changeLlm("llama")

keyboard.keymap=[
    [
        KC.MACRO(macroOpen),KC.MACRO(macroClose),KC.MACRO(macroSummarize),
        KC.MACRO(macroExpand),KC.MACRO(macroHumanize),KC.MACRO(macroGpt),
        KC.MACRO(macroGemini),KC.MACRO(macroLlama),
    ]
]

keyboard.encoder_handler=handleEncoder

# on startup functionaltiy -->
refreshDisp()
blinkLeds()
print("LLMDeck starting")
keyboard.go()
