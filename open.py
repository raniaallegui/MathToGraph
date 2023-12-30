from flask import Flask
import spacy

import re
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
import openai
import requests
from PIL import Image
from io import BytesIO
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
import time
import math
from openai.error import RateLimitError



def words(sentence):
  # Tokenize the sentence into words
  words = word_tokenize(sentence)

  # Tag the words with their part-of-speech
  pos_tags = pos_tag(words)

  # Extract the common nouns and person names from the tagged words
  kelmet = []
  for word, pos in pos_tags:
      if pos.startswith('NN') or pos.startswith('NNP'):
          kelmet.append(word)
      elif pos == 'NNP' and word.istitle():
          kelmet.append(word)

  # Print the extracted common nouns and person names
  return kelmet

def key_words(sentence,noun):

    # Parse the sentence with spacy
    doc = nlp(sentence)

    # Find the noun in the parsed sentence
    noun_token = None
    for token in doc:
        if token.text.lower() == noun.lower():
            noun_token = token
            break

    # If the noun was found, extract related modifiers
    related_modifiers_kbal = []
    related_modifiers_baaed =[]
    if noun_token is not None:
        for child in noun_token.children:
            #print(child.dep_)
            if child.dep_ in ['amod', 'advmod','compound','nmod']:
                related_modifiers_kbal.append(child.text)
            if str(child) in ['of','with']:
                related_modifiers_baaed.append(child.text)
                for weldi in child.children:
                  #print(weldi)
                  related_modifiers_baaed.append(weldi.text)
    mellekhr=' '.join(related_modifiers_kbal+[noun]+related_modifiers_baaed)
    return mellekhr

def extract_action_verb(sentence):
    words = nltk.word_tokenize(sentence)

    # Use the part-of-speech tagger to tag each word with its part of speech
    pos_tags = nltk.pos_tag(words)

    # Extract verbs that denote physical action
    physical_verbs = []
    for word, pos in pos_tags:
        if pos.startswith('VB'):
            synsets = wn.synsets(word, pos=wn.VERB)
            for synset in synsets:
                lexname = synset.lexname()
                if lexname.startswith('verb.motion') or lexname.startswith('verb.contact') or lexname.startswith('verb.perception') or lexname.startswith('verb.change'):
                    physical_verbs.append(word)

    # Check for infinitive verbs that denote physical action
    for i, (word, pos) in enumerate(pos_tags):
        if pos == 'TO' and i > 0:
            prev_word, prev_pos = pos_tags[i-1]
            if prev_word in physical_verbs:
                physical_verbs.append('to ' + prev_word)

    # Print the list of physical verbs
    return list(set(physical_verbs))


def has_verb(words):
    for word in words:
        doc = nlp(word)
        for token in doc:
            if token.pos_ == "VERB":
                return True
    return False
def txt2Im(text):
  # Set up the OpenAI API client
  openai.api_key = "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"

  response = openai.Image.create(
    prompt=text,
    n=1,
    size="256x256"
  )
  # Get the URL of the image from the OpenAI API response
  image_url = response['data'][0]['url']

  # Send a GET request to download the image from the URL
  response = requests.get(image_url)

  # Load the image data from the response into a PIL Image object
  image = Image.open(BytesIO(response.content))

  # Save the image to a file
  #image.save('my_image.png')
  return image

def is_plural(noun):
    lemmatizer = WordNetLemmatizer()
    pos = pos_tag([noun])
    if pos[0][1] == 'NNS' or (pos[0][1] == 'NN' and noun[-1] == 's'):
        return 1
    else:
        return 0


def number_related_to_word(word, sentence):
    # Tokenize the sentence into words
    words = word_tokenize(sentence)

    # Find the index of the given word in the list of words
    index = words.index(word)

    # Check if the previous word is a number
    if index > 0 and words[index-1].isdigit():
        return int(words[index-1])
    else:
        return -1

def is_word(input_str):
    if " " in input_str:
        return 0
    else:
        return 1

def extract_numbers(sentence):
    return re.findall(r'\d+', sentence)

def diviseurs_proches(n):
    diviseurs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            diviseurs.append(i)
            diviseurs.append(n // i)
    diviseurs.sort()
    i = 0
    j = len(diviseurs) - 1
    min_diff = abs(diviseurs[i] - diviseurs[j])
    min_i = i
    min_j = j
    while i < j:
        diff = abs(diviseurs[i] - diviseurs[j])
        if diff < min_diff:
            min_diff = diff
            min_i = i
            min_j = j
        if diff == 0:
            break
        elif diviseurs[i] * diviseurs[j] < n:
            i += 1
        else:
            j -= 1
    return [diviseurs[min_i], diviseurs[min_j]]


def est_premier(n):
    if n < 2:
        return 0
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return 0
    return 1

def generate_white_image(width,height):
  # Create a new image with the desired size and white background
  white_img = Image.new("RGB", (width, height), color="white")
  return white_img

def generate_image_hor1(image,n):
  images = []
  for i in range(n):
      images.append(image)

  new_img = Image.new("RGB", (image.width*n,image.height), color="white")

  x_offset = 0
  for image in images:
      new_img.paste(image, (x_offset, 0))
      x_offset += image.size[0]
  return new_img

def generate_image_ver1(image,n):

  images = []
  for i in range(n):
      images.append(image)


  new_img = Image.new("RGB", (image.width,image.height*n), color="white")

  y_offset = 0
  for image in images:
      new_img.paste(image, (0, y_offset))
      y_offset += image.size[1]

  return new_img


def generate_image_ver2(image1,image2,n):

  images = []
  for i in range(n):
      if i==n//2:
        images.append(image2)
      else:
        images.append(image1)

  new_img = Image.new("RGB", (image1.width,image1.height*n), color="white")

  y_offset = 0
  for image in images:
      new_img.paste(image, (0, y_offset))
      y_offset += image.size[1]

  return new_img


def generate_image_hor2(image,n):
  images = []

  for i in range(n):
      if i == n//2:
        images.append(image)
      else:
        images.append(generate_white_image(image.width,image.height))


  new_img = Image.new("RGB", (image.width*n,image.height), color="white")

  x_offset = 0
  for image in images:
      new_img.paste(image, (x_offset, 0))
      x_offset += image.size[0]
  return new_img

def generate_image_hor3(image,n):
  images = []

  if n%2==1:
    for i in range(n):
      images.append(image)
      new_img = Image.new("RGB", (image.width*n,image.height), color="white")
  else:
    for i in range(n+1):
      if i == n//2:
        images.append(generate_white_image(image.width,image.height))
      else:
        images.append(image)
      new_img = Image.new("RGB", (image.width*(n+1),image.height), color="white")


  x_offset = 0
  for image in images:
      new_img.paste(image, (x_offset, 0))
      x_offset += image.size[0]
  return new_img

def regenarat_image(image,n):
  if est_premier(n):
    return generate_image_ver2(generate_image_hor3(image,diviseurs_proches(n-1)[1]),generate_image_hor2(image,diviseurs_proches(n-1)[1]),diviseurs_proches(n-1)[0]+1).resize((image.width,image.height))
  else:
    return generate_image_ver1(generate_image_hor1(image,diviseurs_proches(n)[1]),diviseurs_proches(n)[0]).resize((image.width,image.height))




def nchlh(problem):
  # Utilisez la fonction split() du module re pour diviser le paragraphe en phrases
  problem_sentences = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', problem)

  khalitni=[]
  for sentence in problem_sentences:
    dour=[]
    mwejaa=words(sentence)
    for ksir in mwejaa:
      dour.append(key_words(sentence,ksir))
    khalitni.append(dour)
  galbi=1
  while(galbi==1):
    galbi=0
    for hossed in khalitni:
      i=0
      while(i<len(hossed)):
        j=0
        while(j<len(hossed)):
          if ((str(hossed[j]) in str(hossed[i])) and (i!=j) or ((j==len(hossed)-1) and (str(hossed[j]) in str(hossed[i])) and str(hossed[j])!=str(hossed[i]))):
            #print(str(hossed[i]),"|",str(hossed[j]))
            hossed.remove(hossed[j])
            galbi=1
          j=j+1
        i=i+1
  khalitni1=[]
  nghochek=[]
  for i in range(len(khalitni)):
    t=0
    b=extract_action_verb(problem_sentences[i])
    if len(khalitni[i])==2 and len(b)==1:
      t=1
      nghochek.append(khalitni[i][0])
      nghochek.append(b[0])
      nghochek.append(khalitni[i][1])
    if t==1:
      khalitni1.append(nghochek)
      nghochek=[]
    else:
      khalitni1.append(khalitni[i])
  khalitni1
  for i in range(len(khalitni1)):
    if khalitni1[i]!=khalitni[i] or has_verb(khalitni1[i]):
      khalitni1[i]=[' '.join(khalitni1[i])]
  khalitni1
  for i in range(len(problem_sentences)):
    for j in range(len(khalitni1[i])):
      if is_word(khalitni1[i][j]):
        if number_related_to_word(khalitni1[i][j],problem_sentences[i])!=-1:
          khalitni1[i][j]=str(number_related_to_word(khalitni1[i][j],problem_sentences[i]))+' '+khalitni1[i][j]
  return khalitni1





app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from app1!"

def my_function(text):
    global nlp
    nlp = spacy.load("en_core_web_sm")
    print(nchlh(text)) 
    khalitni1=nchlh(text)
    wahdin=[]
    khawef=[]
    lhamdoulah=[]
    for khali in khalitni1:
        tsawer=[]
        for k in khali:
            if re.sub(r'\d+\s*', '', k) in khawef and len(extract_numbers(k))==0:
                tsawer.append(wahdin[khawef.index(re.sub(r'\d+\s*', '', k))])
                wahdin.append(wahdin[khawef.index(re.sub(r'\d+\s*', '', k))])
                khawef.append(re.sub(r'\d+\s*', '', k))
            elif re.sub(r'\d+\s*', '', k) in khawef and len(extract_numbers(k))>=1:
                img=wahdin[khawef.index(re.sub(r'\d+\s*', '', k))]
                im=regenarat_image(img,int(extract_numbers(k)[0]))
                tsawer.append(im)
                wahdin.append(img)
                khawef.append(re.sub(r'\d+\s*', '', k))
            else:
                if is_word(k)==1 and  is_plural(k)==0:
                    while True:
                        try:
                            img=txt2Im("one "+k+" clipart")
                            tsawer.append(img)
                            wahdin.append(img)
                            khawef.append(k)
                            break
                        except RateLimitError:
                            time.sleep(1)
                elif len(extract_numbers(k))==1:
                    while True:
                        try:

                            img=txt2Im("one "+re.sub(r'\d+\s*', '', k)+" clipart")
                            im=regenarat_image(img,int(extract_numbers(k)[0]))
                            tsawer.append(im)
                            wahdin.append(img)
                            khawef.append(re.sub(r'\d+\s*', '', k))
                            break
                        except RateLimitError:
                            time.sleep(1)
                else:
                    while True:
                        try:
                            img=txt2Im(k+" clipart")
                            tsawer.append(img)
                            wahdin.append(img)
                            khawef.append(k)
                            break
                        except RateLimitError:
                            time.sleep(1)            
        lhamdoulah.append(tsawer)
    images = []
    for i in range(len(lhamdoulah)):
        for image in lhamdoulah[i]:
            images.append(image)
            print(len(images))
    print("nnnnnnnnnnn")
    pathtsawer=[]
    for i in range(len(images)):
        j=i+1
        image_path = 'static/images/Prob/image'+str(j)+'.png'
        images[i].save(image_path)
        pathtsawer.append(image_path)
    return pathtsawer

if __name__ == '__main__':
    app.run(debug=True)

