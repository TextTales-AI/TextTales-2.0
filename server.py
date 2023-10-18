#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, jsonify, request
import os
import gnews
import openai
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from datetime import datetime
import requests
import datetime
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")

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
  chat_model = ChatOpenAI(model_name='gpt-3.5-turbo-16k') # Must have set API key as env var
  prompt = f"Identify three key themes in the following text an give each theme an informative title. Return each key theme on a new line. This is the text: {text}"
  themes = chat_model.predict(prompt)

  # prompt = f"Based on these three themes {themes} found in this text {text} write a coherent three segment podcast text for a podcaster to read. The listener have already been listening to an introduction so jump right into the segments without introducing them."
  # podcast_transcript = chat_model.predict(prompt)
  
  prompt = f"Based on these three themes {themes} found in this text {text} write a podcast text for a podcaster to read only for theme 1. The listener have already been listening to an introduction of the themes so no introduction is needed. Only generate the text that will be read for theme 1. Dont introduce the podcast or mention the other themes."
  theme_1 = chat_model.predict(prompt)
  prompt = f"Based on these three themes {themes} found in this text {text} write a podcast text for a podcaster to read only for theme 2. The listener have already been listening to an introduction of the themes so no introduction is needed. Only generate the text that will be read for theme 2. Dont introduce the podcast or mention the other themes."
  theme_2 = chat_model.predict(prompt)
  prompt = f"Based on these three themes {themes} found in this text {text} write a podcast text for a podcaster to read only for theme 3. The listener have already been listening to an introduction of the themes so no introduction is needed. Only generate the text that will be read for theme 3. Dont introduce the podcast or mention the other themes."
  theme_3 = chat_model.predict(prompt)
  # print(themes)
  # print(podcast_transcript)
  return themes, theme_1 + theme_2 + theme_3

def gen_intro(town, day, time, w_temp, w_desc, topic, themes):
    # Connect to OpenAI, prompt ChatGPT to summarize the text
    chat_model = ChatOpenAI(model_name='gpt-3.5-turbo-16k') # Must have set API key as env var
    prompt = f"You are going to generate a podcast introduction for the daily news podcast PodPerfect hosted by Zoe. Begin with setting the scene with how the current day is looking. It is {day} and the time is {time} in {town}. The weather is {w_temp} with {w_desc}. Then introduce the {topic}. The three segments in today’s podcast are {themes}. In your response, only include the words Zoe should read and no other text. Make it around 300 words. Begin with “You are listening to PodPerfect – a podcast with me, Zoe, as your AI host.” and end with “Let’s jump right in!”."
    intro = chat_model.predict(prompt)

    prompt = f"You are going to generate a podcast outro for the daily news podcast PodPerfect hosted by Zoe. The three segments in today’s podcast was the following themes {themes}. In your response, only include the words Zoe should read and no other text. Make it around 300 words. End with “You have been listening to PodPerfect – a podcast with me, Zoe your AI host.”"
    outro = chat_model.predict(prompt)
    return intro, outro

app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/create')
def get_create():
    town = "Stockholm"
    days = ["Monday", "Tuesday", "Wednesday", "Thirsday", "Friday", "Saturday", "Sunday"]
    day = days[datetime.datetime.today().weekday()]
    time = "9 a.m"
    topic = request.args.get('topic')
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
    return jsonify(full_text)

app.run(host='0.0.0.0', port=3000)