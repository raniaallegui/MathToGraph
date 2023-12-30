from flask import Flask
import pandas as pd
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import re



app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from app2!"

def similar(input_problem,problems):
    global tokenizer
    global model
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    input_problem = input_problem.lower().replace(' ','')
    inputs1 = tokenizer(input_problem, return_tensors='pt')
    
    with torch.no_grad():
        outputs1 = model(**inputs1)
    
    embeddings1 = outputs1.last_hidden_state.mean(dim=1).numpy()
    max_similarity_score = 0
    most_similar_problem = ""
    for problem in problems:
        problem_text = problem
        terteh=problem_text
        problem_text = problem_text.lower().replace(' ','')
        inputs2 = tokenizer(problem_text, return_tensors='pt')
        with torch.no_grad():
            outputs2 = model(**inputs2)
        embeddings2 = outputs2.last_hidden_state.mean(dim=1).numpy()
        similarity_score = cosine_similarity(embeddings1.reshape(1, -1), embeddings2.reshape(1, -1))[0][0]
        
        if similarity_score > max_similarity_score:
            max_similarity_score = similarity_score
            most_similar_problem = problem_text
            rojla=terteh
    max_similarity_percentage = round(max_similarity_score * 100, 2)
    print("The most similar problem to the input problem is:", rojla)
    print("The percentage of similarity between the two problems is:", max_similarity_percentage, "%")
    return (rojla,max_similarity_percentage)




def compare_strings(string1, string2):
    # Obtenir une liste de tous les mots de chaque chaîne
    words1 = re.findall(r'\w+', string1)
    words2 = re.findall(r'\w+', string2)
    
    # Convertir les mots en ensembles pour l'opération de l'intersection
    set1 = set(words1)
    set2 = set(words2)
    
    # Calculer le nombre de mots communs
    common_words = len(set1.intersection(set2))
    
    return common_words/len(words1)

def score_reponse(rep_vrai,rep_child):
  lamen=compare_strings(rep_child[0],rep_vrai[0])
  if len(rep_child)>2:
    kbal=[]
    for i in range(len(rep_vrai)-1):
        khales=[]
        for j in range(len(rep_child)-1):
            khales.append(compare_strings(rep_child[j],rep_vrai[i]))
        kbal.append(max(khales))
    t=0
    print('kk')
    for i in range(len(rep_child)-2):

      if eval(rep_child[i])!=eval(rep_child[i+1]):
        t=t+1
    if lamen>0.9 and t==0:
      if rep_vrai[-1]==rep_child[-1] :
        print("Bravo votre réponse est correcte!")
        return 1
    elif sum(kbal)/len(kbal)>0.5 and t==0:
      print('hh')
      return lamen
    elif sum(kbal)/len(kbal)>0.5 and t>0:
      print('ff')
      return 1/(t+1)*sum(kbal)/len(kbal)
    else:
      print('gg')
      return 0
  elif len(rep_child)==2:
    if lamen>0.9:
      if rep_vrai[-1]==rep_child[-1] and eval(rep_child[0])==eval(rep_vrai[-1]):
        print("Bravo votre réponse est correcte!")
        return 1
      elif eval(rep_child[0])==eval(rep_child[1]):
        return 0.5
      else :
        return 0
    else :
      return 0
  else:
    if rep_vrai[-1]==rep_child[-1]:
      return 1
    else:
      return 0


if __name__ == '__main__':
    app.run(debug=True)
