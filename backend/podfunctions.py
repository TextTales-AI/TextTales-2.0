import os
from newspaper import Config
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from elevenlabs import voices, generate, play, save
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from pydub import AudioSegment
from moviepy.editor import concatenate_audioclips, AudioFileClip
import gradio as gr
import gnews

# Set API keys
ELEVEN_API_KEY = "531f744b0717aa59ee58e7e90f930c6"
os.environ["OPENAI_API_KEY"] = "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"

# Set user agent for newspaper
config = Config()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
config.browser_user_agent = user_agent

# Initialize chat model
chat_model = ChatOpenAI(model_name='gpt-3.5-turbo-16k')  # Make sure to set the API key as an environment variable

class PerfecPod:
    def __init__(self):
        self.text = ""
    
    def concatenate_audio_moviepy(self, audio_clip_paths, output_path):
        """Concatenates several audio files into one audio file using MoviePy
        and save it to `output_path`. Note that extension (mp3, etc.) must be added to `output_path`"""
        clips = [AudioFileClip(c) for c in audio_clip_paths]
        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile(output_path)
    
    def podify(self, user_prompt, num_minutes=False, voice="Adam"):


        # return user_prompt + str(num_minutes)

        prompt = "Can you create a documentary/news broadcast/podcast/fantasy story about this input? Respond only by returning 'YES' or explain why it does not work. Input = {}".format(user_prompt)
        response = chat_model.predict(prompt)
        if "YES" != response:
            return print(response)

        num_words = num_minutes*135

        prompt = "What category would you classify this input trying to create? Respond just by returning 'NEWS', 'STORY' or 'DOCUMENTARY' Input = {}".format(user_prompt)
        category = chat_model.predict(prompt)
        
        if category == "NEWS":
            pass
        elif category == "DOCUMENTARY":

            if not os.path.exists("documentary_audio"):
                os.makedirs("documentary_audio")

            prompt = "Create the outline/structure for a {} word long documentary about {}. Specify how many words each section should have. Return your answer in this format '*****Topic 1, *****Topic 2, *****Topic 3'".format(num_words, user_prompt) 
            response = chat_model.predict(prompt)
            split_response = response.split('*****')
            sections = []
            for part in split_response:
                if len(part) > 10:
                    sections.append(part)

            file_names = []
            for i in range(len(sections)):
                print(i)
                if i == 0:
                    prompt = "Write the introduction for this documentary about {}, focus on this part {}. Use approximatly the same number of words that are specified. ".format(user_prompt, sections[0]) 
                else:
                    prompt = "You are writing a text about {} and now you are going to write about this sub-topic {}. Use approximatly the same number of words that are specified. Start with 'Part {}: ' + the headline for this sub-topic".format(user_prompt, sections[i], i) 
                response = chat_model.predict(prompt)
                audio = generate(text=response, voice="Adam", model="eleven_monolingual_v1", api_key=ELEVEN_API_KEY)
                save(audio, "documentary_audio/documentary_in_{}_mins_{}.wav".format(num_minutes, i))
                self.text += "\n" + response + "\n"
                file_names.append("documentary_audio/documentary_in_{}_mins_{}.wav".format(num_minutes, i))
                file_names.append("sound_effects/original_transition.wav")

            self.concatenate_audio_moviepy(file_names, "documentary_audio/documentary_about_{}_in_{}_mins.wav".format(user_prompt, num_minutes))

        else:

            # Save audiofile
            if not os.path.exists("story_audio"):
                os.makedirs("story_audio")

            prompt = "Create the outline/chapters for a {} word long story about {}. Specify how many words each section should have. Return your answer in this format '*****Chapter 1, *****Chapter 2, *****Chapter 3'".format(num_words, user_prompt) 
            response = chat_model.predict(prompt)
            prompt = "Summarise what the story is about: {}".format(response)
            topic = chat_model.predict(prompt)

            split_response = response.split('*****')
            sections = []
            for part in split_response:
                if len(part) > 10:
                    sections.append(part)

            file_names = []
            summary = ""
            for i in range(len(sections)):
                print(i)
                
                prompt = "You are writing a story about {} and now you are going to write about this chapter {}. This has happened so far in the story: '{}'. Use approximatly the same number of words that are specified. Start with 'Chapter X: ' + the headline for this chapter".format(topic, sections[i], summary) 
                response = chat_model.predict(prompt)
                print(response)
                print('*****')
                prompt = "Summarise: {}".format(response)
                summary = chat_model.predict(prompt)
                #audio = generate(text=response, voice="Adam", model="eleven_monolingual_v1", api_key=ELEVEN_API_KEY)
                #save(audio, "story_audio/story_about_{}_in_{}_mins_{}.wav".format(user_prompt, num_minutes, i))
                #self.text += "\n" + response + "\n"
                
                #file_names.append("story_audio/story_about_{}_in_{}_mins_{}.wav".format(user_prompt, num_minutes, i))
                #file_names.append("sound_effects/original_transition.wav")

            #self.concatenate_audio_moviepy(file_names, "story_audio/story_about_{}_in_{}_mins.wav".format(user_prompt, num_minutes))
    
        return self.text



#podify("I want to listen to an inspring story about someone who broke their legs when skiing, and then fought their way back to win the olympic gold. make the story 5 minutes long", 5)
#podify("Create a story where the pirates discover one letter in each chapter, and these letters forms a word that is the code for the treasure", "Podcast med två röster", 10, "J SWE k")
#podify("Create a bedtime story for my 8 year old daughter that includes horses, princesses, princes and it should be female empowering", "Story", 10, "J SWE k")
#podify("Israels historia", "Podcast med två röster", 2, "J SWE k")
    