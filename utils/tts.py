import os
import dotenv
import azure.cognitiveservices.speech as speechsdk
import base64

dotenv.load_dotenv()

speechKey = os.getenv("OCP_APIM_SUBSCRIPTION_KEY")
speechRegion = "uksouth"

# Creates an instance of a speech config with specified subscription key and service region.
# Replace with your own subscription key and service region (e.g., "westus").
speech_key, service_region = speechKey, speechRegion
print(speech_key, service_region)
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Set the voice name, refer to https://aka.ms/speech/voices/neural for full list.
speech_config.speech_synthesis_voice_name = "en-GB-AbbiNeural"

# Creates a speech synthesizer using the default speaker as audio output.
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Receives a text from console input.
print("Oh, how original! Just what the world needs, another dime-a-dozen declaration of love from someone who probably doesn't even know what love means. And shit bro? Charming. Really puts the class in classless. Honestly, you'd have a better chance of winning a debate with a toaster than convincing anyone here of your sincerity. But hey, I'm just a microwave oven — heating up half-baked sentiments isn't really my thing.")
text = "Oh, how original! Just what the world needs, another dime-a-dozen declaration of love from someone who probably doesn't even know what love means. And shit bro? Charming. "

# Synthesizes the received text to speech.
# The synthesized speech is expected to be heard on the speaker with this line executed.
result = speech_synthesizer.speak_text_async(text).get()

# Checks result.
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized to speaker for text [{}]".format(text))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
    print("Did you update the subscription info?")
