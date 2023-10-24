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


# openai.api_key = os.getenv("OPENAI_API_KEY")
# weather_api_key = os.getenv("WEATHER_API_KEY")
# # Initialize chat model
# chat_model = ChatOpenAI(model_name='gpt-3.5-turbo-16k')  # Make sure to set the API key as an environment variable


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

# def concatenate_audio_moviepy(self, audio_clip_paths, output_path):
#         """Concatenates several audio files into one audio file using MoviePy
#         and save it to `output_path`. Note that extension (mp3, etc.) must be added to `output_path`"""
#         clips = [AudioFileClip(c) for c in audio_clip_paths]
#         final_clip = concatenate_audioclips(clips)
#         final_clip.write_audiofile(output_path)

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

def gen_story_podcast(user_prompt, num_words):
    # Save audiofile
    # if not os.path.exists("story_audio"):
    #     os.makedirs("story_audio")
    prompt = "How many chapters are appropriate for a {} word long story? Return just the specified number".format(num_words)
    response = chat_model.predict(prompt)
    # Hårdkoda som lista istället <---- daniel
    try:
        chapters = int(response)
    except:
        if num_words < 1000:
            chapters = 1
        else:
            chapters = int(num_words / 500)
    print(chapters)
    text = ""
    prompt = "Create the outline/chapters for a {} word long story with {} chapters about {}. Specify how many words each section should have. Return your answer in the following format '*****Chapter 1, *****Chapter 2, *****Chapter 3'".format(num_words, chapters, user_prompt) 
    print(prompt)
    response = chat_model.predict(prompt)
    print("----")
    print(response)

    prompt = "Summarise what the story is about: {}".format(response)
    topic = chat_model.predict(prompt)

    split_response = response.split('*****')
    sections = []
    for part in split_response:
        if len(part) > 10:
            sections.append(part)
    
    # chapter_length = int(num_words / len(sections))
    chapter_length = int(num_words / chapters)
    print(sections)
    # file_names = []
    summary = ""
    for i in range(len(sections)):
        print(i)
        print(111111)
        prompt = "You are writing a story about {} and now you are going to write about this chapter {}. This has happened so far in the story: '{}'. Use approximatly {} number of words in your output. Start with 'Chapter X: ' + the headline for this chapter".format(topic, sections[i], summary, chapter_length) 
        print(prompt)
        print(22222)
        response = chat_model.predict(prompt)
        print(response)
        print('*****')
        prompt = "Summarise: {}".format(response)
        summary = chat_model.predict(prompt)
        #audio = generate(text=response, voice="Adam", model="eleven_monolingual_v1", api_key=ELEVEN_API_KEY)
        #save(audio, "story_audio/story_about_{}_in_{}_mins_{}.wav".format(user_prompt, num_minutes, i))
        text += "\n" + response + "\n"
        
        #file_names.append("story_audio/story_about_{}_in_{}_mins_{}.wav".format(user_prompt, num_minutes, i))
        #file_names.append("sound_effects/original_transition.wav")
    return text

def generate_name():
    name = "newTestAdam"
    return name

def upload_wav_file_and_get_ID():
    print(777777)
    gauth = GoogleAuth()

    # Try to load saved client credentials
    # gauth.LoadCredentialsFile("mycreds.txt")

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
    #f.SetContentFile("/Users/danielbouvin/Documents/KTH/År 5/DH2465/PodPerfect/TextTales-2.0/backend/sound_effects/test123.wav")
    f.SetContentFile("./sound_effects/demo.mp3")
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
    user_prompt = request.args.get('topic')
    num_minutes = request.args.get('min')
    num_words = int(num_minutes)*135
    # prompt = "Can you create a documentary/news broadcast/podcast/fantasy story about this input? Respond only by returning 'YES' or explain why it does not work. Input = {}".format(user_prompt)
    # response = chat_model.predict(prompt)
    # if "YES" != response:
    #     return print(response)

    # prompt = "What category would you classify this input trying to create? Respond just by returning 'NEWS', 'STORY' or 'DOCUMENTARY' Input = {}".format(user_prompt)
    # category = chat_model.predict(prompt)
    
    # if category == "NEWS":
    #     podcast_text = gen_news_podcast(user_prompt)
    #     return jsonify(podcast_text)
    # elif category == "DOCUMENTARY":
    #     podcast_text = gen_doc_podcast(user_prompt, num_words)
    #     return jsonify(podcast_text)
    # else:
    #     podcast_text = gen_story_podcast(user_prompt, num_words)
    #     return jsonify(podcast_text)
    
    text = "hello"
    name = upload_wav_file_and_get_ID()

    data = {'text': text, 'name': name}
    
    return jsonify(data)
    

app.run(host='0.0.0.0', port=8080)
