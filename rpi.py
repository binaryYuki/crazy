import os
import pyaudio
from google.cloud import speech
import queue
import RPi.GPIO as GPIO
import time
import requests  # Import requests to send data to an API
import threading
import json

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
button_pin = 18  # GPIO 18
relay_pin = 17
led_pin = 27

GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(relay_pin, GPIO.OUT)

# Set Google Cloud Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/user/Downloads/tts/broadcast-c6b76-57be70c737f6.json"

# Audio recording parameters
RATE = 44100
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream:
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1, rate=self._rate, input=True, frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            yield chunk

def control_led(duration):
	def turn_on_led():
		GPIO.output(led_pin, GPIO.HIGH)
		GPIO.output(relay_pin, GPIO.HIGH)
		time.sleep(duration)
		GPIO.output(relay_pin, GPIO.LOW)
		GPIO.output(led_pin, GPIO.LOW)
		
	led_thread = threading.Thread(target=turn_on_led)
	led_thread.start()
	
def get_text_reply(transcripts):
    api_url = 'http://40.81.144.221:8000/api/v1/response' 
    data = {'text': transcripts}
    
    try:
        response = requests.get(api_url, json=data)
        response.raise_for_status() 
        print(f'Successfully sent to API: {response.json()}')
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error sending to API: {e}')

def get_time_reply(transcripts):
    api_url = 'http://40.81.144.221:8000/api/v1/analyze' 
    data = {'text': transcripts}
    
    try:
        response = requests.get(api_url, json=data)
        response.raise_for_status() 
        print(f'Successfully sent to API: {response.json()}')
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f'Error sending to API: {e}')
        
def transcribe_streaming():
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code='en-US'
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )

    while True:
        if GPIO.input(button_pin):
            temp = []  # Initialize temp list for each button press
            print("Button pressed. Starting to record...")

            with MicrophoneStream(RATE, CHUNK) as stream:
                requests_gen = (speech.StreamingRecognizeRequest(audio_content=content) for content in stream.generator())
                responses = client.streaming_recognize(streaming_config, requests_gen)

                for response in responses:
                    for result in response.results:
                        if result.is_final:  # Process only final results
                            transcript = result.alternatives[0].transcript
                            print(f'Transcript: {transcript}')
                            temp.append(transcript)

                    # Check if the button is released
                    if not GPIO.input(button_pin):
                        print("Button released. Stopping the stream...")
                        break  # Exit the response loop

            print("Sending data to API...")
            print('this is the data being sent', '. '.join(temp))
            text_reply = get_text_reply(''.join(temp))  # Send collected transcripts to API
            
            
            time_reply = get_time_reply(''.join(temp))
            

            print("espeak -ven-us+f4 -s170 ' " + text_reply['response'] + " ' ")
            
            # write the text_reply['response'] to a file
            with open('response.txt', 'w') as f:
                f.write(text_reply['response'])

            # say the file with espeak
            #os.system("espeak -ven-us+f4 -s170 -f response.txt")
            #print( "echo '" + text_reply['response'] +"' /home/user/piper/piper --model /home/user/piper/en_US-amy-medium.onnx --output_file /home/user/Downloads/tts/welcome.wav")
            #os.system("echo '" + text_reply['response'] +"' /home/user/piper/piper --model /home/user/piper/en_US-amy-medium.onnx --output_file /home/user/Downloads/tts/welcome.wav")
            
            os.system("/home/user/piper/piper --model /home/user/piper/en_US-amy-medium.onnx --output_file welcome.wav --rate 2.0 < /home/user/Downloads/tts/response.txt")
            control_led(int(time_reply['time']))
            
            os.system("aplay welcome.wav")
            
            
            
        else:
            print('Waiting for button press...')
            time.sleep(0.1)  # Short sleep to avoid busy-waiting

transcribe_streaming()
