#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, jsonify, request, send_file
import os
import gnews
import openai
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from datetime import datetime
import requests
import datetime
load_dotenv()
from pydrive.auth import GoogleAuth 
from pydrive.drive import GoogleDrive
from moviepy.editor import concatenate_audioclips, AudioFileClip
import uuid
from elevenlabs import voices, generate, play, save

openai.api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
# # Initialize chat model
chat_model = ChatOpenAI(model_name='gpt-3.5-turbo-16k')  # Make sure to set the API key as an environment variable

class Podcast:
    def __init__(self, user_prompt, num_minutes, category):
        self.ID = generate_name()
        self.user_prompt = user_prompt
        self.num_minutes = int(num_minutes)
        self.num_words = int(num_minutes) * 135
        self.category = category
        self.text_list = []
        self.sound_file_name = self.ID + ".wav"
        self.drive_name = ""

    def get_ID(self):
        return self.ID

    def get_drive_name(self):
        return self.drive_name
    
    def gen_story_podcast(self):
        
        if self.num_words < 1000:
            prompt = "Create a story about '{}'. The story should be approximately {} number of words".format(self.user_prompt, self.num_words)
            self.text_list = [chat_model.predict(prompt)]
            print("--------")
            print(self.text_list)
        else:
            chapters = int(self.num_words / 300)
            prompt = "Create a detailed outline for a story about '{}' with {} scenes. Return your answer in the following format:".format(self.user_prompt, str(chapters*3))
            for i in range(1, 3*chapters+1):
                prompt += "\nScene {}:".format(str(i))

            outline = chat_model.predict(prompt)
            scene_list = []
            for i in range(1, chapters*3+1):
                scene_before_index = outline.index("Scene {}".format(str(i)))
                if i < chapters*3:
                    scene_after_index = outline.index("Scene {}".format(str(i+1)))
                    scene = outline[scene_before_index:scene_after_index]
                else:
                    scene = outline[scene_before_index:]
                scene_list.append(scene)

            prompt = "Specify the characters and in what scene they enter the story based on this outline:\n{}\n\nReturn in the format:\nName of character - Description - Scene Number".format(outline)
            characters = chat_model.predict(prompt)
            extended_scenes = []

            for i in range(chapters):
                number_of_scenes = 3
                response_format = "Return in the format:\nPart {}:\nPart {}:\nPart {}:".format(str(i*3+1), str(i*3+2), str(i*3+3))
                scenes = scene_list[i*3] + "\n" + scene_list[i*3+1] + "\n" + scene_list[i*3+2]
                if i < chapters - 1:
                        scenes += "\n" + scene_list[i*3+3]
                        response_format += "\nPart {}:".format(str(i*3+4))
                        number_of_scenes = 4
                
                #prompt = "Turn these {} scenes into storytelling format, add details, return just the text:\n{}\n\nHere is a list of characters and in what scene they will or have been introduced:\n{}\n\n{}".format(str(number_of_scenes), scenes, characters, response_format)
                prompt = "Here are the story's characters and in what scenes they appear:\n{}\n\nRewrite the following scenes into a plain text story that can written in a book. Add unnecessary details so the story feels more alive:\n{}\n\n{}".format(characters, scenes, response_format)
                response = chat_model.predict(prompt)

                k = 0
                for j in range(i*3+1,i*3+number_of_scenes+1):
                    k += 1
                    scene_before_index = response.lower().index("part {}".format(str(j)))
                    if j < i*3+number_of_scenes:
                        scene_after_index = response.lower().index("part {}".format(str(j+1)))
                        scene = response[scene_before_index:scene_after_index]
                    else:
                        scene = response[scene_before_index:]
                    
                    if k < 4:
                        extended_scenes.append(scene)

            cleaned_text = []
            for row in extended_scenes:
                split_row = row.split("\n")[1:]  # Remove the first element
                restored_row = "\n".join(split_row)  # Join the remaining elements with newline
                restored_row = restored_row.strip("\n")
                cleaned_text.append(restored_row)

            self.text_list = cleaned_text
            print("--------")
            print(self.text_list)

    def audiofy_story(self, voice="Adam", sound_effect_name="fairytale"):

        if not os.path.exists("story_audio"):
            os.makedirs("story_audio")
        
        
        file_names = []
        # for i in range(len(self.text_list)):
        #     audio = generate(text=self.text_list[i], voice=voice, model="eleven_monolingual_v1", api_key=ELEVEN_API_KEY)
        #     save(audio, "./story_audio/story_{}_{}.wav".format(self.ID, str(i)))

        #     file_names.append("./story_audio/story_{}_{}.wav".format(self.ID, str(i)))
        #     file_names.append("./sound_effects/{}.wav".format(sound_effect_name))
        

        # file_names = ["./sound_effects/fairytale.wav","./sound_effects/fairytale.wav"]
        file_names = ["./sound_effects/original_transition.wav","./sound_effects/original_transition.wav"]
        concatenate_audio_moviepy(file_names, "./story_audio/{}".format(self.sound_file_name))

    def upload_wav_file_and_get_ID(self):
        print(777777)
        gauth = GoogleAuth()

        # Try to load saved client credentials
        gauth.LoadCredentialsFile("mycreds.txt")

        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.GetFlow()
            gauth.flow.params.update({'access_type': 'offline'})
            gauth.flow.params.update({'approval_prompt': 'force'})
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()

        # Save the current credentials to a file
        gauth.SaveCredentialsFile("mycreds.txt")  

        drive = GoogleDrive(gauth)

        title = generate_name() + ".txt"
        team_drive_id = '1WdeZhQ_vegXPMA-JeoM0pldAOKbCCVcx'
        parent_folder_id = '1TtWk3uo0jTC0BR2CAlaH8DgcRtp0hDCb'
        f = drive.CreateFile({
            'title': title,
            'parents': [{
                'kind': 'drive#fileLink',
                'teamDriveId': team_drive_id,
                'id': parent_folder_id
            }]
        })
        f.SetContentFile("./story_audio/" + self.sound_file_name)
        f.Upload(param={'supportsTeamDrives': True})

        files = drive.ListFile({"q": "'" + parent_folder_id + "' in parents and mimeType!='application/vnd.google-apps.folder'"}).GetList()

        name = ""
        for file in files:
            if file['title'] == title:
                name = file['id']

        self.drive_name = name
    
    def list_to_text(self):
        text = ""
        for row in self.text_list:
            text += row + "\n"
        return text


def gen_article_text(topic, env="prod"):
    article_titles = list()
    article_body = list()
    if(env == "prod"):
        # google_news = gnews.GNews(period='7d', max_results=10)
        google_news = gnews.GNews(language='en', country='Sweden', period='7d', max_results=10)
        news_response = google_news.get_news(topic) # En lista av artikelobjekt, article.text, article.title
        for news in news_response:
            full_article = google_news.get_full_article(news['url'])
            if(full_article and (full_article.title and full_article.text)):
                if(len(article_body) < 3):
                    article_titles.append(full_article.title)
                    article_body.append(full_article.text)
        with open('./tmp/articles.txt', 'w') as f:   
            for i in range(len(article_titles)):
                if(i != 0):
                    f.write(f"********\n")
                f.write(f"{article_titles[i]}\n")
                f.write(f"********\n")
                f.write(f"{article_body[i]}\n")
    elif(env == "test"):
        with open('./tmp/articles.txt') as f:
            lines = f.readlines()
            lines = ''.join([line.strip() for line in lines])
            lines = lines.split("********")
            for i in range(len(lines)):
                line = lines[i]
                if(i % 2 == 0):
                    article_titles.append(line)
                else:
                    article_body.append(line)
    # print(article_titles)
    # print(article_body)
    combined_text = ""
    for article in article_body:
        combined_text += article
    
    return combined_text

def get_weather(city):
    # url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid=8368401dc9a8d9bee4eeafa222ec5047&units=metric'
    res = requests.get(url)
    data = res.json()
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind = data['wind']['speed']
    description = data['weather'][0]['description']
    temp = int(data['main']['temp'])

    # print('Temperature:',temp,'°C')
    # print('Wind:',wind)
    # print('Pressure: ',pressure)
    # print('Humidity: ',humidity)
    # print('Description:',description)
    return temp, description

def themes_and_sumamry(text):  
  prompt = f"Identify three key themes in the following text an give each theme an informative title. Return each key theme on a new line. This is the text: {text}"
  themes = chat_model.predict(prompt)

  # prompt = f"Based on these three themes {themes} found in this text {text} write a coherent three segment podcast text for a podcaster to read. The listener have already been listening to an introduction so jump right into the segments without introducing them."
  # podcast_transcript = chat_model.predict(prompt)
  
  prompt = f"Based on these three themes {themes} found in this text {text} write a short podcast text for a podcaster to read only for theme 1. The listener have already been listening to an introduction of the themes so no introduction is needed. Only generate the text that will be read for theme 1. Dont introduce the podcast or mention the other themes."
  theme_1 = chat_model.predict(prompt)
  prompt = f"Based on these three themes {themes} found in this text {text} write a short podcast text for a podcaster to read only for theme 2. The listener have already been listening to an introduction of the themes so no introduction is needed. Only generate the text that will be read for theme 2. Dont introduce the podcast or mention the other themes."
  theme_2 = chat_model.predict(prompt)
  prompt = f"Based on these three themes {themes} found in this text {text} write a short podcast text for a podcaster to read only for theme 3. The listener have already been listening to an introduction of the themes so no introduction is needed. Only generate the text that will be read for theme 3. Dont introduce the podcast or mention the other themes."
  theme_3 = chat_model.predict(prompt)
  # print(themes)
  # print(podcast_transcript)
  return themes, theme_1 + theme_2 + theme_3

def concatenate_audio_moviepy(audio_clip_paths, output_path):
        """Concatenates several audio files into one audio file using MoviePy
        and save it to `output_path`. Note that extension (mp3, etc.) must be added to `output_path`"""
        clips = [AudioFileClip(c) for c in audio_clip_paths]
        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile(output_path)

def gen_intro(town, day, time, w_temp, w_desc, topic, themes):
    # Connect to OpenAI, prompt ChatGPT to summarize the text
    prompt = f"You are going to generate a podcast introduction for the daily news podcast PodPerfect hosted by Zoe. Begin with setting the scene with how the current day is looking. It is {day} and the time is {time} in {town}. The weather is {w_temp} with {w_desc}. Then introduce the {topic}. The three segments in today’s podcast are {themes}. In your response, only include the words Zoe should read and no other text. Make it around 300 words. Begin with “You are listening to PodPerfect – a podcast with me, Zoe, as your AI host.” and end with “Let’s jump right in!”."
    intro = chat_model.predict(prompt)

    # prompt = f"You are going to generate a podcast outro for the daily news podcast PodPerfect hosted by Zoe. The three segments in today’s podcast was the following themes {themes}. In your response, only include the words Zoe should read and no other text. Make it around 300 words. End with “You have been listening to PodPerfect – a podcast with me, Zoe your AI host.”"
    # outro = chat_model.predict(prompt)
    outro = ""
    return intro, outro

def gen_news_podcast(topic):
    town = "Stockholm"
    days = ["Monday", "Tuesday", "Wednesday", "Thirsday", "Friday", "Saturday", "Sunday"]
    day = days[datetime.datetime.today().weekday()]
    time = "6 a.m"
    
    print("topic")
    print(topic)
    text = gen_article_text(topic, "prod")
    print("articles")
    themes, podcast_transcript = themes_and_sumamry(text)
    print("summ")
    w_temp, w_desc = get_weather(town)
    print("waether")
    intro, outro = gen_intro(town, day, time, w_temp, w_desc, topic, themes)
    full_text = intro + "\n" + podcast_transcript + "\n" + outro
    print(full_text)
    return full_text

### Vet inte om denna behövs (merge conflict)
def gen_doc_podcast(user_prompt, num_words):
    # if not os.path.exists("documentary_audio"):
    #     os.makedirs("documentary_audio")
    text = ""
    prompt = "Create the outline/structure for a {} word long documentary about {}. Specify how many words each section should have. Return your answer in this format '*****Topic 1, *****Topic 2, *****Topic 3'".format(num_words, user_prompt) 
    response = chat_model.predict(prompt)
    split_response = response.split('*****')
    sections = []
    for part in split_response:
        if len(part) > 10:
            sections.append(part)
    chapter_length = int(num_words / len(sections))
    file_names = []
    for i in range(len(sections)):
        print(i)
        if i == 0:
            prompt = "Write the introduction for this documentary about {}, focus on this part {}. Use approximatly {} number of words in your output. ".format(user_prompt, sections[0], chapter_length) 
        else:
            prompt = "You are writing a text about {} and now you are going to write about this sub-topic {}. Use approximatly {} number of words in your output. Start with 'Part {}: ' + the headline for this sub-topic".format(user_prompt, sections[i], chapter_length, i) 
        response = chat_model.predict(prompt)
        # audio = generate(text=response, voice="Adam", model="eleven_monolingual_v1", api_key=ELEVEN_API_KEY)
        # save(audio, "documentary_audio/documentary_in_{}_mins_{}.wav".format(num_minutes, i))
        text += "\n" + response + "\n"
        # file_names.append("documentary_audio/documentary_in_{}_mins_{}.wav".format(num_minutes, i))
        # file_names.append("sound_effects/original_transition.wav")
    # concatenate_audio_moviepy(file_names, "documentary_audio/documentary_about_{}_in_{}_mins.wav".format(user_prompt, num_minutes))
    
    return text
### Vet inte om denna behövs (merge conflict)
def gen_story_podcast(self, user_prompt, num_words):
        
    if num_words < 1000:
        prompt = "Create a story about '{}'. The story should be approximately {} number of words".format(user_prompt, num_words)
        return chat_model.predict(prompt)
    else:
        chapters = int(num_words / 300)
        prompt = "Create a detailed outline for a story about '{}' with {} scenes. Return your answer in the following format:".format(user_prompt, str(chapters*3))
        for i in range(1, 3*chapters+1):
            prompt += "\nScene {}:".format(str(i))

        outline = chat_model.predict(prompt)
        scene_list = []
        for i in range(1, chapters*3+1):
            scene_before_index = outline.index("Scene {}".format(str(i)))
            if i < chapters*3:
                scene_after_index = outline.index("Scene {}".format(str(i+1)))
                scene = outline[scene_before_index:scene_after_index]
            else:
                scene = outline[scene_before_index:]
            scene_list.append(scene)

        prompt = "Specify the characters and in what scene they enter the story based on this outline:\n{}\n\nReturn in the format:\nName of character - Description - Scene Number".format(outline)
        characters = chat_model.predict(prompt)
        extended_scenes = []

        for i in range(chapters):
            number_of_scenes = 3
            response_format = "Return in the format:\nNarrative {}:\nNarrative {}:\nNarrative {}:".format(str(i*3+1), str(i*3+2), str(i*3+3))
            scenes = scene_list[i*3] + "\n" + scene_list[i*3+1] + "\n" + scene_list[i*3+2]
            if i < chapters - 1:
                    scenes += "\n" + scene_list[i*3+3]
                    response_format += "\nNarrative {}:".format(str(i*3+4))
                    number_of_scenes = 4
            
            prompt = "Turn these {} scenes into narratives and expand them:\n{}\n\nHere is a list of characters and in what scene they will or have been introduced:\n{}\n\n{}".format(str(number_of_scenes), scenes, characters, response_format)
            response = chat_model.predict(prompt)

            k = 0
            for j in range(i*3+1,i*3+number_of_scenes+1):
                k += 1
                scene_before_index = response.lower().index("narrative {}".format(str(j)))
                if j < i*3+number_of_scenes:
                    scene_after_index = response.lower().index("narrative {}".format(str(j+1)))
                    scene = response[scene_before_index:scene_after_index]
                else:
                    scene = response[scene_before_index:]
                
                if k < 4:
                    extended_scenes.append(scene)

        cleaned_text = []
        for row in extended_scenes:
            split_row = row.split("\n")[1:]  # Remove the first element
            restored_row = "\n".join(split_row)  # Join the remaining elements with newline
            cleaned_text.append(restored_row)

        return cleaned_text

def generate_name():
    # Generate a unique ID
    unique_id = str(uuid.uuid4())
    return unique_id

def temp_gen():
    print(777777)
    gauth = GoogleAuth()

    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.GetFlow()
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")  

    drive = GoogleDrive(gauth)

    title = generate_name() + ".mp3"
    team_drive_id = '1WdeZhQ_vegXPMA-JeoM0pldAOKbCCVcx'
    parent_folder_id = '1TtWk3uo0jTC0BR2CAlaH8DgcRtp0hDCb'
    f = drive.CreateFile({
        'title': title,
        'parents': [{
            'kind': 'drive#fileLink',
            'teamDriveId': team_drive_id,
            'id': parent_folder_id
        }]
    })
    f.SetContentFile("./notebooks/output/test.mp3")
    f.Upload(param={'supportsTeamDrives': True})

    files = drive.ListFile({"q": "'" + parent_folder_id + "' in parents and mimeType!='application/vnd.google-apps.folder'"}).GetList()

    name = ""
    for file in files:
        if file['title'] == title:
            name = file['id']

    return name

app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/create')
def get_create():
    print(00000)
    
    # Argument fetched from url params
    user_prompt = request.args.get('topic') # User input can be any string
    num_minutes = request.args.get('min') # Time [0-5, 5-10, 10-15]
    podcast_type = request.args.get("style") # style ["NEWS", "STORY"]
    # num_words = int(num_minutes)*135

    # Pausar detta för tillfället
    # prompt = "Can you create a documentary/news broadcast/podcast/fantasy story about this input? Respond only by returning 'YES' or explain why it does not work. Input = {}".format(user_prompt)
    # response = chat_model.predict(prompt)
    # if "YES" != response:
    #     return print(response)

    new_podcast = Podcast(user_prompt, num_minutes, podcast_type)
    
    if podcast_type == "NEWS":
        # Todo fix
        print("IN NEWS")
        podcast_name = temp_gen()
        data = {'text': "TODO", 'name': podcast_name}
        return jsonify(data)
    elif podcast_type == "STORY":
        new_podcast.gen_story_podcast()
        new_podcast.audiofy_story()
        new_podcast.upload_wav_file_and_get_ID()


    data = {'text': new_podcast.list_to_text(), 'name': new_podcast.get_drive_name()}
    
    return jsonify(data)
    

app.run(host='0.0.0.0', port=8080)
