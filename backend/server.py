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
from pydrive.auth import GoogleAuth 
from pydrive.drive import GoogleDrive
from moviepy.editor import concatenate_audioclips, AudioFileClip
import uuid
from elevenlabs import voices, generate, play, save
import pandas as pd
import tiktoken
from openai.embeddings_utils import get_embedding
from ast import literal_eval
import numpy as np
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from pydub import AudioSegment
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
# # Initialize chat model
chat_model = ChatOpenAI(model_name='gpt-3.5-turbo-16k')  # Make sure to set the API key as an environment variable

class Podcast:
    def __init__(self, user_prompt, num_minutes, category):
        self.ID = str(uuid.uuid4())
        self.user_prompt = user_prompt
        self.num_minutes = int(num_minutes)
        self.num_words = int(num_minutes) * 135
        self.category = category
        self.outputPath = "./" + category.lower() + "_audio/"
        self.text_list = []
        self.sound_file_name = self.ID + ".mp3"
        self.drive_name = ""
        self.articlesDF = pd.DataFrame(columns=['article_title','article_body','embeddings'])

        # New Daniel
        self.sound_file_names = []
        self.voice = "Adam"
        self.topic = ""
        self.genre = ""
        self.title = ""

        # News part
        self.cleaned_intro = ""
        self.cleaned_outro = ""
        self.cleaned_segment_1 = ""
        self.cleaned_segment_2 = ""
        self.cleaned_segment_3 = ""

    def get_ID(self):
        return self.ID

    def get_drive_name(self):
        return self.drive_name
    
    def gen_story_podcast(self):
        
        if self.num_words < 1000:
            prompt = "Create a story about '{}'. The story should be approximately {} number of words".format(self.user_prompt, self.num_words)
            self.text_list = [chat_model.predict(prompt)]
            prompt = "Create a title for this story:\n'{}'".format(self.text_list)
            self.title = chat_model.predict(prompt)
            print("--------")
            print(self.text_list)
        else:
            chapters = int(self.num_words / 300)
            prompt = "Create a detailed outline for a story about '{}' with {} scenes. Return your answer in the following format:".format(self.user_prompt, str(chapters*3))
            for i in range(1, 3*chapters+1):
                prompt += "\nScene {}:".format(str(i))

            outline = chat_model.predict(prompt)
            prompt = "Create a title for this story:\n'{}'".format(outline)
            self.title = chat_model.predict(prompt)
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

    def audiofy_story(self, sound_effect_name="fairytale"):
        
            if not os.path.exists("./story_audio"):
                os.makedirs("./story_audio")

            # Intro
            self.story_create_intro()

            # Story
            for i in range(len(self.text_list)):
                audio = generate(text=self.text_list[i], voice=self.voice, model="eleven_multilingual_v2", api_key=ELEVEN_API_KEY)
                save(audio, "./story_audio/story_{}_{}.wav".format(self.ID, str(i)))

                self.sound_file_names.append("./story_audio/story_{}_{}.wav".format(self.ID, str(i)))
                # Sound between segments
                # self.sound_file_names.append("./sound_effects/{}.wav".format(sound_effect_name))

            # Outro
            self.story_create_outro()

            # self.sound_file_names = ["./sound_effects/fairytale.wav","./sound_effects/fairytale.wav"]
            # self.sound_file_names = ["./sound_effects/original_transition.wav","./sound_effects/original_transition.wav"]

            audio_files_pydub = []
            for file_name in self.sound_file_names:
                loaded_audio_in_pydub = AudioSegment.from_file(file_name, format="mp3")
                audio_files_pydub.append(loaded_audio_in_pydub)

            combined = audio_files_pydub.pop(0)
            for pydub_audio in audio_files_pydub:
                combined += pydub_audio
            print("./story_audio/{}".format(self.sound_file_name))
            combined.export("./story_audio/{}".format(self.sound_file_name), format="mp3")

            #self.concatenate_audio_moviepy(self.sound_file_names, "./story_audio/{}".format(self.sound_file_name))

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

        title = self.ID
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

        f.SetContentFile(self.outputPath + self.sound_file_name)
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

    def concatenate_audio_moviepy(self, audio_clip_paths, output_path):
            """Concatenates several audio files into one audio file using MoviePy
            and save it to `output_path`. Note that extension (mp3, etc.) must be added to `output_path`"""
            clips = [AudioFileClip(c) for c in audio_clip_paths]
            final_clip = concatenate_audioclips(clips)
            final_clip.write_audiofile(output_path)

    def story_create_intro(self):
            # Generic intro
            intro = "This story is brought to you by Pod Perfect. We hope you enjoy."
            if not os.path.exists("./story_audio/intro.wav"):
                print("Does not exist. Creating intro")
                audio = generate(text=intro, voice="Daniel", model="eleven_multilingual_v2", api_key=ELEVEN_API_KEY)
                save(audio, "story_audio/intro.wav")
            
            self.sound_file_names.append("./story_audio/intro.wav")

            if self.genre == "fantasy":
                pass
            elif self.genre == "science fiction":
                pass
            elif self.genre == "mystery":
                pass
            elif self.genre == "romance":
                pass
            elif self.genre == "horror":
                pass
            elif self.genre == "thriller/suspense":
                pass
            elif self.genre == "adventure":
                pass
            elif self.genre == "historical fiction":
                pass
            elif self.genre == "drama":
                pass
            elif self.genre == "comedy":
                pass
            elif self.genre == "action":
                pass
            elif self.genre == "crime":
                pass
            elif self.genre == "dystopian":
                pass
            elif self.genre == "young adult (ya)":
                pass
            elif self.genre == "paranormal":
                pass
            elif self.genre == "western":
                pass
            elif self.genre == "satire":
                pass
            elif self.genre == "biography":
                pass
            elif self.genre == "autobiography":
                pass
            elif self.genre == "non-fiction":
                pass
            else:
                self.sound_file_names.append("./sound_effects/story_intro.wav")

            # Append suitable intro music        
            # self.sound_file_names.append("./story_audio/intro.wav")

            # Title
            audio = generate(text=self.title + "\n\n", voice=self.voice, model="eleven_multilingual_v2", api_key=ELEVEN_API_KEY)
            save(audio, "./story_audio/story_{}_{}.wav".format(self.ID, self.title.replace(" ", "_")))
            self.sound_file_names.append("./story_audio/story_{}_{}.wav".format(self.ID, self.title.replace(" ", "_")))

    def story_create_outro(self):
        # Generic outro
        outro = "\n\n\nThis story was brought to you by Pod Perfect. We hope you enjoyed it and that you will come back and listen to more."
        if not os.path.exists("./story_audio/outro.wav"):
            print("Does not exist. Creating intro")
            audio = generate(text=outro, voice="Daniel", model="eleven_multilingual_v2", api_key=ELEVEN_API_KEY)
            save(audio, "story_audio/outro.wav")
        
        self.sound_file_names.append("./story_audio/outro.wav")
        if self.genre == "fantasy":
            pass
        elif self.genre == "science fiction":
            pass
        elif self.genre == "mystery":
            pass
        elif self.genre == "romance":
            pass
        elif self.genre == "horror":
            pass
        elif self.genre == "thriller/suspense":
            pass
        elif self.genre == "adventure":
            pass
        elif self.genre == "historical fiction":
            pass
        elif self.genre == "drama":
            pass
        elif self.genre == "comedy":
            pass
        elif self.genre == "action":
            pass
        elif self.genre == "crime":
            pass
        elif self.genre == "dystopian":
            pass
        elif self.genre == "young adult (ya)":
            pass
        elif self.genre == "paranormal":
            pass
        elif self.genre == "western":
            pass
        elif self.genre == "satire":
            pass
        elif self.genre == "biography":
            pass
        elif self.genre == "autobiography":
            pass
        elif self.genre == "non-fiction":
            pass
        else:
            self.sound_file_names.append("./sound_effects/story_intro.wav")

    # NEWS
    def scrape_news_from_topic_and_cluster_and_embedd(self):
        article_titles = list()
        article_body = list()

        google_news = gnews.GNews(language='en', country='Sweden', period='7d', max_results=10)
        news_response = google_news.get_news(self.user_prompt) # En lista av artikelobjekt, article.text, article.title
        for news in news_response:
            # print("before")
            full_article = google_news.get_full_article(news['url'])
            # print("after")
            if(full_article and (full_article.title and full_article.text)):
                article_titles.append(full_article.title)
                article_body.append(full_article.text)

        self.articlesDF["article_title"] = article_titles
        self.articlesDF["article_body"] = article_body
        self.articlesDF["combined"] = (
            "Title: " + self.articlesDF.article_title.str.strip() + "; Content: " + self.articlesDF.article_body.str.strip()
        )
        # embedding model parameters
        embedding_model = "text-embedding-ada-002"
        embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
        max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191
        encoding = tiktoken.get_encoding(embedding_encoding)
        self.articlesDF["embeddings"] = self.articlesDF.combined.apply(lambda x: get_embedding(x, engine=embedding_model))

        # Save to csv for test purposes
        self.articlesDF.to_csv("tmp/embeddings.csv")

        # Cluster
        datafile_path = "tmp/embeddings.csv"
        self.articlesDF = pd.read_csv(datafile_path)

        self.articlesDF["embeddings"] = self.articlesDF.embeddings.apply(literal_eval).apply(np.array)  # convert string to numpy array

        matrix = np.vstack(self.articlesDF.embeddings.values)
        matrix.shape

        n_clusters = 3

        kmeans = KMeans(n_clusters=n_clusters, init="k-means++", random_state=42, n_init=10)
        kmeans.fit(matrix)
        labels = kmeans.labels_
        self.articlesDF["Cluster"] = labels
        self.articlesDF.groupby("Cluster")#.Score.mean().sort_values()
 
    # NEWS
    def gen_titles(self, titles):
        titles = ''.join(titles) # Converts list of strings to a combined string
        # print(titles)
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
            "role": "system",
            "content": "You are a system that gets a list of titles of articles that will be explained in a podcast. Based on the titles you will generate a new title that fits this podcast segment. Your output should have this format: \"\"\"Insert title here\"\"\".\n"
            },
            {
            "role": "user",
            "content": titles
            }
        ],
        temperature=1,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        return response['choices'][0]['message']['content']

    # NEWS
    def create_news_pod(self):
        segment_1_title = self.gen_titles(self.articlesDF.loc[self.articlesDF['Cluster'] == 0]["article_title"].to_list()).replace('"""', '') # Replace to remove format form prompt
        segment_2_title = self.gen_titles(self.articlesDF.loc[self.articlesDF['Cluster'] == 1]["article_title"].to_list()).replace('"""', '')
        segment_3_title = self.gen_titles(self.articlesDF.loc[self.articlesDF['Cluster'] == 2]["article_title"].to_list()).replace('"""', '')

        intro, outro = self.news_intro_outro_gen(segment_1_title, segment_2_title, segment_3_title)

        segment_1_body = self.news_gen_segment(self.articlesDF.loc[self.articlesDF['Cluster'] == 0]["article_body"].to_list()).replace('"""', '') # Replace to remove format form prompt
        segment_2_body = self.news_gen_segment(self.articlesDF.loc[self.articlesDF['Cluster'] == 1]["article_body"].to_list()).replace('"""', '')
        segment_3_body = self.news_gen_segment(self.articlesDF.loc[self.articlesDF['Cluster'] == 2]["article_body"].to_list()).replace('"""', '')

        # Workaround to remove the special characters in string
        with open("./tmp/intro.txt", "w") as text_file:
            text_file.write(intro)

        with open("./tmp/outro.txt", "w") as text_file:
            text_file.write(outro)

        with open("./tmp/segment1.txt", "w") as text_file:
            text_file.write(segment_1_title + "\n\n" + segment_1_body)

        with open("./tmp/segment2.txt", "w") as text_file:
            text_file.write(segment_2_title + "\n\n" + segment_2_body)

        with open("./tmp/segment3.txt", "w") as text_file:
            text_file.write(segment_3_title + "\n\n" + segment_3_body)

        with open("./tmp/intro.txt", "r") as text_file:
            self.cleaned_intro = text_file.read()

        with open("./tmp/outro.txt", "r") as text_file:
            self.cleaned_outro = text_file.read()

        with open("./tmp/segment1.txt", "r") as text_file:
            self.cleaned_segment_1 = text_file.read()

        with open("./tmp/segment2.txt", "r") as text_file:
            self.cleaned_segment_2 = text_file.read()

        with open("./tmp/segment3.txt", "r") as text_file:
            self.cleaned_segment_3 = text_file.read()

        self.text_list.append(self.cleaned_intro)
        self.text_list.append(self.cleaned_segment_1)
        self.text_list.append(self.cleaned_segment_2)
        self.text_list.append(self.cleaned_segment_3)
        self.text_list.append(self.cleaned_outro)
    
    # News
    def news_intro_outro_gen(self, segment_1_title, segment_2_title, segment_3_title):
        town = "Stockholm"
        days = ["Monday", "Tuesday", "Wednesday", "Thirsday", "Friday", "Saturday", "Sunday"]
        day = days[datetime.datetime.today().weekday()]
        time = "9 a.m"
        w_temp, w_desc = self.get_weather(town)

        input = f"This is the data about the day: town: {town}, day: {day}, time: {time}, temperature: {w_temp}, weather description: {w_desc}. And this is what the podcast will cover: {segment_1_title}, {segment_2_title}, {segment_3_title}"

        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
            "role": "system",
            "content": 'You are a system that generates the introduction to the news podcast PodPerfect run by Robin.  You get some information about the current day and the topic Robin will talk about and you will combine this information into an opening segment or introduction to the podcast. Your output should follow this format and this is the output you should give with the """Insert Text Here""" replaced: From PodPerfect, I am Robin, bringing you this personalized podcast. """Insert Text Here""" Lets jump right in!'
            },
            {
            "role": "user",
            "content": input
            }
        ],
        temperature=1,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        response2 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
            "role": "system",
            "content": 'You are a system that generates the outro to the news podcast PodPerfect run by Robin. You will get the introduction to the podcast as input. Always end with "This episode was created by PodPerfect, your personalised podcast platform!" Your output should follow this format with """Insert Text Here""" replaced: """Insert Text Here""".'
            },
            {
            "role": "user",
            "content": input
            }
        ],
        temperature=1,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        return response['choices'][0]['message']['content'], response2['choices'][0]['message']['content']

    # NEWS
    def get_weather(self, city):
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

    # NEWS
    def news_gen_segment(self, articles):
        articles = ''.join(articles) # Converts list of strings to a combined string
        max_tokens_for_input = 7000
        max_chars_for_input = max_tokens_for_input * 4 # One token is roughly 4 chars
        
        # Shorten it to fit length of input to produce best results
        articles = (articles[:max_chars_for_input] + '..') if len(articles) > max_chars_for_input else articles
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
            "role": "system",
            "content": 'You are a system that gets a body of articles and your job is to create a podcast segment out of it covering the main topics and themes in the text. Your output should only be the text that the podcaster will read out loud and nothing else. Try to make it around 7000 tokens. Your output should be in the following format: """INSERT TEXT HERE"""'
            },
            {
            "role": "user",
            "content": articles
            }
        ],
        temperature=1,
        max_tokens=9000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        return response['choices'][0]['message']['content']

    # NEWS
    def audiofy_news(self, sound_effect_name="news_transition"):
        # Error handling for Mr Bouvängan
        if not os.path.exists("./tmp"):
            os.makedirs("./tmp")

        if not os.path.exists("./news_audio"):
            os.makedirs("./news_audio")

        intro_audio = generate(text=self.cleaned_intro, voice=self.voice, model="eleven_multilingual_v2", api_key=ELEVEN_API_KEY)
        save(intro_audio,'./tmp/intro.wav')

        outro_audio = generate(text=self.cleaned_outro, voice=self.voice, model="eleven_multilingual_v2", api_key=ELEVEN_API_KEY)
        save(outro_audio,'./tmp/outro.wav')

        segment1_audio = generate(text=self.cleaned_segment_1[:1000], voice=self.voice, model="eleven_multilingual_v2", api_key=ELEVEN_API_KEY)
        save(segment1_audio,'./tmp/segment1.wav')

        segment2_audio = generate(text=self.cleaned_segment_2[:1000], voice=self.voice, model="eleven_multilingual_v2", api_key=ELEVEN_API_KEY)
        save(segment2_audio,'./tmp/segment2.wav')

        segment3_audio = generate(text=self.cleaned_segment_3[:1000], voice=self.voice, model="eleven_multilingual_v2", api_key=ELEVEN_API_KEY)
        save(segment3_audio,'./tmp/segment3.wav')
    
        sound_intro = AudioSegment.from_file("./tmp/intro.wav", format="mp3")
        sound_segment1 = AudioSegment.from_file("./tmp/segment1.wav", format="mp3")
        sound_segment2 = AudioSegment.from_file("./tmp/segment2.wav", format="mp3")
        sound_segment3 = AudioSegment.from_file("./tmp/segment3.wav", format="mp3")
        sound_outro = AudioSegment.from_file("./tmp/outro.wav", format="mp3")
        sound_transition = AudioSegment.from_file("./sound_effects/news_transition.mp3", format="mp3")
        # sound1, with sound2 appended (use louder instead of sound1 to append the louder version)

        # sound_intro = sound_intro.fade_out(3000)
        combined = sound_transition + sound_intro + sound_transition + sound_segment1 + sound_transition + sound_segment2 + sound_transition + sound_segment3 + sound_transition + sound_outro + sound_transition
        combined.export("./news_audio/" + self.ID + ".mp3", format="mp3")

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
    data = {}
    if podcast_type == "NEWS":
        new_podcast.voice = "Bella" # Kanske fixa snyggare sen
        # Todo fix
        print("1")
        new_podcast.scrape_news_from_topic_and_cluster_and_embedd()
        print("2")
        new_podcast.create_news_pod()
        print("3")
        new_podcast.audiofy_news()
        print("4")
        new_podcast.upload_wav_file_and_get_ID()
        print("5")
    elif podcast_type == "STORY":
        new_podcast.gen_story_podcast()
        new_podcast.audiofy_story()
        new_podcast.upload_wav_file_and_get_ID()
        
    data = {'text': new_podcast.list_to_text(), 'name': new_podcast.get_drive_name()}
    
    return jsonify(data)
    

app.run(host='0.0.0.0', port=8080)


# def embedd_articles(self):
#     # embedding model parameters
#     embedding_model = "text-embedding-ada-002"
#     embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
#     max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191
#     encoding = tiktoken.get_encoding(embedding_encoding)
#     self.articlesDF["embeddings"] = self.articlesDF.combined.apply(lambda x: get_embedding(x, engine=embedding_model))

#     # Save to csv for test purposes
#     # self.articlesDF.to_csv("tmp/embeddings.csv")

# def cluster(self):
#     # datafile_path = "tmp/embeddings.csv"
#     # df = pd.read_csv(datafile_path)
#     self.articlesDF["embeddings"] = self.articlesDF.embeddings.apply(literal_eval).apply(np.array)  # convert string to numpy array
#     matrix = np.vstack(self.articlesDF.embeddings.values)
#     matrix.shape

#     n_clusters = 3

#     kmeans = KMeans(n_clusters=n_clusters, init="k-means++", random_state=42, n_init=10)
#     kmeans.fit(matrix)
#     labels = kmeans.labels_
#     self.articlesDF["Cluster"] = labels
#     self.articlesDF.groupby("Cluster")#.Score.mean().sort_values()
