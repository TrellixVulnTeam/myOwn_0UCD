# Голосовой ассистент
import os
import time
import speech_recognition as sr
from fuzzywuzzy import fuzz
import pyttsx3
import datetime

# настройки
opts = {
    "alias": ('джарвис', 'жарвис', 'шарвис', 'джарвиз', 'жарвиз', 'шарвиз'),
    "tbr": ('скажи', 'расскажи', 'покажи', 'сколько', 'произнеси', 'давай', 'дай'),
    "cmd": {
        "time": ('текущее время', 'сейчас времени', 'который час'),
        "radio": ('включи музыку', 'воспроизведи радио', 'включи радио'),
        "stupid1": ('анекдот', 'рассмеши меня', 'ты знаешь анекдоты')
    }
}


# функции
def speak(what):
    print(what)
    speak_engine.say(what)
    speak_engine.runAndWait()
    speak_engine.stop()


def callback(recognizer, audio):
    try:
        voice = recognizer.recognize_google(audio, language="ru-RU").lower()
        print("[log] Распознано: " + voice)

        if voice.startswith(opts["alias"]):
            # обращаются к боту
            cmd = voice

            for x in opts['alias']:
                cmd = cmd.replace(x, "").strip()

            for x in opts['tbr']:
                cmd = cmd.replace(x, "").strip()

            # распознаем и выполняем команду
            cmd = recognize_cmd(cmd)
            execute_cmd(cmd['cmd'])

    except sr.UnknownValueError:
        print("[log] Голос не распознан!")
    except sr.RequestError as e:
        print("[log] Неизвестная ошибка, проверьте интернет!")


def recognize_cmd(cmd):
    RC = {'cmd': '', 'percent': 0}
    for c, v in opts['cmd'].items():

        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > RC['percent']:
                RC['cmd'] = c
                RC['percent'] = vrt

    return RC


def execute_cmd(cmd):
    if cmd == 'time':
        # сказать текущее время
        now = datetime.datetime.now()
        speak("Сейчас " + str(now.hour) + ":" + str(now.minute))

    elif cmd == 'radio':
        # воспроизвести радио
        os.system("D:\\Jarvis\\res\\radio_record.m3u")

    elif cmd == 'stupid1':
        # рассказать анекдот
        speak("Мой разработчик не научил меня анекдотам ... Ха ха ха")

    else:
        print('Команда не распознана, повторите!')

    main()


# запуск
# r = sr.Recognizer()
# m = sr.Microphone(device_index=1)


speak_engine = pyttsx3.init()

# Только если у вас установлены голоса для синтеза речи!
voices = speak_engine.getProperty('voices')
speak_engine.setProperty('voice', voices[0].id)

# forced cmd test
# speak("Мой разработчик не научил меня анекдотам ... Ха ха ха")

speak("Добрый день, повелитель")
speak("Джарвис слушает")


def main():
    with sr.Microphone(device_index=1) as source:
        sr.Recognizer().pause_threshold = 1
        sr.Recognizer().adjust_for_ambient_noise(source, duration=1)

    sr.Recognizer().listen_in_background(sr.Microphone(device_index=1), callback)


while True:
    time.sleep(1)  # infinity loop
    main()
