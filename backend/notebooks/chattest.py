from pydub import AudioSegment
from elevenlabs import generate, play, set_api_key, save
from scipy.io import wavfile
import time



##Här genereras en elevenlabs-grej och sedan 
# voice = generate(
#     text="Hi! I'm the world's most advanced text-to-speech system, made by elevenlabs.",
#     voice="Bella"
# )
# #rate,content = wavfile.read("halvminut.wav")

### Här skrivs en fil över med nya elevlabs. Den kan läsas av pydub
# with open("genPodcast.mpeg", "wb") as f2:
#     f2.write(voice)




start_time=time.time()
# Load the sound file and the music
sound_file = AudioSegment.from_file("Pinedax.wav", format="wav")
print("Pinedax:")
print(time.time()-start_time)
start_time=time.time()

# sound_file = AudioSegment.from_file("test.wav", format="wav")
music = AudioSegment.from_file("./music/herewithyou.mp3", format="mp3")
#music = AudioSegment.from_file("./music/Blue State.wav", format="wav")
print("music:")
print(time.time()-start_time)
start_time=time.time()

# Ensure the sound and music have the same sample rate
music = music.set_frame_rate(sound_file.frame_rate)
# You can adjust the volume of the music if needed
music = music - 10  # Reduce the volume by 10 dB

print("set rate + adjust volume")


print(time.time()-start_time)
start_time=time.time()



# Add the music to the sound file
start_time=time.time()

combined_audio = sound_file.overlay(music)
print("Combining:")
print(time.time()-start_time)


# Export the combined audio to a new file
start_time=time.time()

combined_audio.export("combined_audio.wav", format="wav")
print("export:")
print(time.time()-start_time)

