from flask import Flask, render_template, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import redirect
from PIL import Image
import os
import re
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta



from open import my_function,txt2Im
from similarity import similar,score_reponse

from gtts import gTTS
from playsound import playsound
# create the extension

# create the app
app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()


# configure the SQLite database, relative to the app instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/Math'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

class Kid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    classe = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(10))  # add the sexe column here
    image_path = db.Column(db.String(80))
    score = db.Column(db.Float)
    

    def __init__(self, FirstName, LastName, classe, gender, image,score=0):  # update the constructor
        self.FirstName = FirstName
        self.LastName = LastName
        self.classe = classe
        self.email = FirstName +'.'+ LastName + '@MathtoGraphie.tn'
        self.password = FirstName + '@' + LastName
        self.gender = gender  # initialize the sexe attribute here
        self.image_path=image
        self.score=score
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(10))  # add the sexe column here
    image_path = db.Column(db.String(80))

    def __init__(self, FirstName, LastName, classe, email, password, gender, image):  # update the constructor
        self.FirstName = FirstName
        self.LastName = LastName
        self.classe = classe
        self.email = email
        self.password = password
        self.gender = gender  # initialize the sexe attribute here
        self.image_path=image

class Classe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))

    def __init__(self,name):  # update the constructor
        self.Name =name

class KTC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idTeacher = db.Column(db.Integer)
    idKid = db.Column(db.Integer)
    idClasse = db.Column(db.Integer)

    def __init__(self,idTeacher,idKid,idClasse):  # update the constructor
        self.idTeacher=idTeacher
        self.idKid=idKid
        self.idClasse=idClasse

class KRP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idKid = db.Column(db.Integer)
    idProb = db.Column(db.Integer)
    Reponse = db.Column(db.String(150))
    score = db.Column(db.Float)


    def __init__(self,idKid,idProb,score):  # update the constructor
        self.idKid=idKid
        self.idProb=idProb
        self.idProb=idProb
        self.score=score
class TP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idTeacher = db.Column(db.Integer)
    idProb = db.Column(db.Integer)
    
    def __init__(self,idTeacher,idProb):  # update the constructor
        self.idTeacher=idTeacher
        self.idProb=idProb
        

        
class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Problem = db.Column(db.String(500))
    Reponse = db.Column(db.String(150))
    classe = db.Column(db.String(50))
    operation = db.Column(db.String(100))
    diff = db.Column(db.Integer)
    situation =db.Column(db.String(10))

    def __init__(self, Problem, Reponse, classe,situation="still"): 
        self.Problem = Problem
        self.Reponse = Reponse
        self.classe = classe 
        operation = []
        diff=0
        my_list=re.split(r"\n|\r|=", Reponse)
        repa=[element for element in my_list if element != '']
        for rep in repa:
            if '+' in rep :
                operation.append("addition")
                diff=diff+0 
            if '-' in rep :
                operation.append("substraction")
                diff=diff+1
            if '*' in rep :
                operation.append("multipllication")
                diff=diff+2
            if '/' in rep :
                operation.append("division")
                diff=diff+3
        self.operation = str(operation)
        self.diff = diff
        self.situation=situation

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Problem = db.Column(db.String(500))
    Reponse = db.Column(db.String(150))
    operation = db.Column(db.String(100))
    diff = db.Column(db.Integer)

    def __init__(self, Problem, Reponse): 
        self.Problem = Problem
        self.Reponse = Reponse
        operation = []
        diff=0
        my_list=re.split(r"\n|\r|=", Reponse)
        repa=[element for element in my_list if element != '']
        for rep in repa:
            if '+' in rep :
                operation.append("addition")
                diff=diff+0 
            if '-' in rep :
                operation.append("substraction")
                diff=diff+1
            if '*' in rep :
                operation.append("multipllication")
                diff=diff+2
            if '/' in rep :
                operation.append("division")
                diff=diff+3
        self.operation = str(operation)
        self.diff = diff





  
with app.app_context():
    db.create_all()

   # user1 = Kid("Loulou", "Nounou", "4ds3")
    #db.session.add(user1)
    #db.session.commit()

    #Routes mtaa teacher 

@app.route('/teacherdash/<int:teacher_id>')
def dashteacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    if teacher is None:
        return "teacher not found"
    else:
        print(teacher.id)
        a= url_for('static', filename=teacher.image_path)
        results=KTC.query.filter_by(idTeacher=teacher_id).with_entities(KTC.idClasse).distinct().all()
        if results is None:
            return "classes not found"
        else:
            print(results)
            idclasses=[result[0] for result in results]
            classes=[]
            for i in idclasses:
                classes.append(Classe.query.filter_by(id=i).first())
            print(classes)
            return render_template('baseTeacher.html',teacher_path=a,classes=classes)




@app.route('/class/<int:class_id>')
def show_class(class_id):
    print(teacher_id_global)
    print(class_id)
    classe_id_global=class_id
    print(classe_id_global)
    class_name = Classe.query.filter_by(id=class_id).first().Name
    if class_name is None:
        return "class not found" 
    else:
        print(class_name)   
        kids =Kid.query.filter_by(classe=class_name).all()
        if kids is None:
            return "kids not found"
        else:
            print(kids)
            teacher = Teacher.query.get_or_404(teacher_id_global)
            if teacher is None:
                return "teacher not found"
            else:            
                a= url_for('static', filename=teacher.image_path)
                results=KTC.query.filter_by(idTeacher=teacher_id_global).with_entities(KTC.idClasse).distinct().all()
                if results is None:
                    return "class not found"
                else:
                    print(results)
                    idclasses=[result[0] for result in results]
                    classes=[]
                    for i in idclasses:
                        classes.append(Classe.query.filter_by(id=i).first())
                    print(classes)
                    for hozn in kids:
                        hozn.image_path='/'+hozn.image_path
                    print(kids[0].image_path)    
                    return render_template('dashboard.html',kids=kids,teacher_path=a,classes=classes)


 

@app.route('/add_Prob', methods=['POST'])
def add_Prob():
    if "Add" in request.form:
    # Get the kid's information from the form
        classe = request.form['classetou']
        problem = request.form['problem']
        reponse = request.form['reponse']
        print(classe)
        print(problem)
        my_list=re.split(r"\n|\r|=", reponse)
        rep=[element for element in my_list if element != '']
        print(rep)
        prob = Portfolio(Problem=problem,Reponse=str(rep),classe=classe)
        db.session.add(prob)
        db.session.commit()
        tp=TP(idTeacher=teacher_id_global,idProb=prob.id)
        db.session.add(tp)
        db.session.commit()
        teacher = Teacher.query.get_or_404(teacher_id_global)
        if teacher is None:
            return "teacher not found"
        else:
            a= url_for('static', filename=teacher.image_path)
            results=KTC.query.filter_by(idTeacher=teacher_id_global).with_entities(KTC.idClasse).distinct().all()
            if results is None:
                return "class not found"
            else:
                print(results)
                idclasses=[result[0] for result in results]
                classes=[]
                for i in idclasses:
                    classes.append(Classe.query.filter_by(id=i).first())
                print(classes)
                sout=TP.query.filter_by(idTeacher=teacher_id_global).with_entities(TP.idProb).distinct().all()
                if sout is None:
                    return "Problems not found"
                else:
                    idProb=[sou[0] for sou in sout]
                    probs=[]
                    for i in idProb:
                        p=Portfolio.query.filter_by(id=i).first()
                        if p is not None:
                            if p.situation=="still":
                                probs.append(p)
                
                    print(probs)
                    return render_template('Portfolio.html',teacher_path=a,probs=probs,classes=classes)

@app.route('/ajout_kid')
def ajoutKids():
    return render_template('ajoutkid.html')
@app.route('/generation_image')
def generation():
    return render_template('generation_image.html')

@app.route('/portfolio')
def portfolio():
    teacher = Teacher.query.get_or_404(teacher_id_global)
    if teacher is None:
        return "teacher not found"
    else:
        print(teacher.id)
        a= url_for('static', filename=teacher.image_path)
        probs = Portfolio.query.filter_by(situation="still").all()
        if probs is None:
            return "problems not found"
        else:
            print(probs)
            results=KTC.query.filter_by(idTeacher=teacher_id_global).with_entities(KTC.idClasse).distinct().all()
            if results is None:
                return "class not found"
            else:
                print(results)
                idclasses=[result[0] for result in results]
                classes=[]
                for i in idclasses:
                    classes.append(Classe.query.filter_by(id=i).first())
                print(classes)
                sout=TP.query.filter_by(idTeacher=teacher_id_global).with_entities(TP.idProb).distinct().all()
                if sout is None:
                    return "problems not found"
                else:
                    idProb=[sou[0] for sou in sout]
                    probs=[]
                    for i in idProb:
                        p=Portfolio.query.filter_by(id=i).first()
                        if p is not None:
                            if p.situation=="still":
                                probs.append(p)
                    return render_template('Portfolio.html',teacher_path=a,probs=probs,classes=classes)




@app.route('/')
def home():
    return render_template('index.html')
@app.route('/dashboard')
def dashboard():
    kids=Kid.query.all()
    return render_template('dashboard.html',kids=kids)

@app.route('/interface_kid')
def interface_kid():
    return render_template('interface_kid.html',open_modal=2)

    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')



@app.route('/add_kid', methods=['POST'])
def add_kid():
    # Get the kid's information from the form
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    class_name = request.form['classi']
    gender = request.form['gender']
    image_file = request.files['image']
    
    filename = image_file.filename
    image_path = 'static/images/Kids/'+ filename # change this line to specify your desired path
    print(image_file)
    image_file.save(image_path)

    # Create a new Kid object and add it to the database
    kid = Kid(FirstName=first_name, LastName=last_name, classe=class_name,gender=gender,image=image_path)
    db.session.add(kid)
    db.session.commit()
    kid1=Kid.query.filter_by(FirstName=first_name,LastName=last_name).first()
    classe=Classe.query.filter_by(Name=class_name).first()
    ktc=KTC(idTeacher=teacher_id_global,idKid=kid1.id,idClasse=classe.id)
    db.session.add(ktc)
    db.session.commit()
    teacher = Teacher.query.get_or_404(teacher_id_global)
    if teacher is None:
        return "teacher not found"
    else:
        a= url_for('static', filename=teacher.image_path)
        kids =Kid.query.filter_by(classe=class_name).all()
        if kids is None:
            return "kids not found"
        else:
            results=KTC.query.filter_by(idTeacher=teacher_id_global).with_entities(KTC.idClasse).distinct().all()
            if results is None:
                return "class not found"
            else:
                print(results)
                idclasses=[result[0] for result in results]
                classes=[]
                for i in idclasses:
                    classes.append(Classe.query.filter_by(id=i).first())
                return render_template('dashboard.html',kids=kids,teacher_path=a,classes=classes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    kid = Kid.query.filter_by(email=email, password=password).first()
    print(kid)
    teacher = Teacher.query.filter_by(email=email, password=password).first()
    if kid is None:
        print('bahhhhh')
        global teacher_id_global
        teacher_id_global=teacher.id
        results=KTC.query.filter_by(idTeacher=teacher_id_global).with_entities(KTC.idClasse).distinct().all()
        print(results)
        idclasses=[result[0] for result in results]
        classes=[]
        for i in idclasses:
            classes.append(Classe.query.filter_by(id=i).first())
        print(classes)
        
        
        
        return redirect(url_for('dashteacher', teacher_id=teacher.id,classes=classes))
    else:
        global kid_id_global
        kid_id_global=kid.id
        return render_template('/interface_kid.html')
    



@app.route('/delete_kid/<int:kid_id>', methods=['POST'])
def delete_kid(kid_id):
    kid = Kid.query.get_or_404(kid_id)
    if kid is None:
        return "kid not found"
    else:
        db.session.delete(kid)
        db.session.commit()
        ktc=KTC.query.filter_by(idKid=kid_id).first()
        if ktc is None:
            return "class not found"
        else:
            classe_id_global=ktc.idClasse
            db.session.delete(ktc)
            db.session.commit()
            return redirect(f'/class/{classe_id_global}')

@app.route('/find_Prob', methods=['POST','GET'])
def find_Prob():
    if "Find" in request.form:
        operation=[]
        c1=False
        c2=False
        c3=False
        c4=False
        multiplication = request.form.get('multiplication')
        addition = request.form.get('addition')
        division = request.form.get('division')
        substraction = request.form.get('substraction')
        if addition:
            operation.append("addition")
            c1=True
        if substraction:
            operation.append("substraction")
            c2=True
        if multiplication:
            operation.append("multiplication")
            c3=True
        if division:
            operation.append("division")
            c4=True
        print('jjjjjjjjjjjjjjjjjjj')
        print(operation)
        probs1 = Problem.query.filter_by().limit(5).all()
        probs=[]
        for p in probs1:
            print(p.operation)
            print(type(p.operation))
            if eval(p.operation)==operation:
                probs.append(p)
        print(probs)
        j=random.randrange(len(probs))
        k=probs[j].Problem
        b=probs[j].Reponse
        global zahra
        zahra=[]
        zahra.append(k)
        zahra.append(b)
        openmodal = True
        teacher = Teacher.query.get_or_404(teacher_id_global)
        a= url_for('static', filename=teacher.image_path)
        results=KTC.query.filter_by(idTeacher=teacher_id_global).with_entities(KTC.idClasse).distinct().all()
        idclasses=[result[0] for result in results]
        classes=[]
        for i in idclasses:
            classes.append(Classe.query.filter_by(id=i).first())
        return render_template('baseTeacher.html',k=k,b=b,openmodal=openmodal,teacher_path=a,classes=classes,c1=c1,c2=c2,c3=c3,c4=c4)
    
@app.route('/add_to_portfolio/<int:classe_id>', methods=['POST','GET'])
def add_to_portfolio(classe_id):
    classe=Classe.query.get_or_404(classe_id)
    prob = Portfolio(Problem=zahra[0],Reponse=str(zahra[1]),classe=classe.Name)
    db.session.add(prob)
    db.session.commit()
    prob1 = Portfolio.query.filter_by(Problem=zahra[0]).first()
    tp=TP(idTeacher=teacher_id_global,idProb=prob1.id)
    db.session.add(tp)
    db.session.commit()
    teacher = Teacher.query.get_or_404(teacher_id_global)
    a= url_for('static', filename=teacher.image_path)
    results=KTC.query.filter_by(idTeacher=teacher_id_global).with_entities(KTC.idClasse).distinct().all()
    print(results)
    idclasses=[result[0] for result in results]
    classes=[]
    for i in idclasses:
        classes.append(Classe.query.filter_by(id=i).first())
    print(classes)
    sout=TP.query.filter_by(idTeacher=teacher_id_global).with_entities(TP.idProb).distinct().all()
    idProb=[sou[0] for sou in sout]
    probs=[]
    for i in idProb:
        p=Portfolio.query.filter_by(id=i).first()
        if p is not None:
            if p.situation=="still":
                probs.append(p)
    
    print(probs)
    return render_template('Portfolio.html',teacher_path=a,probs=probs,classes=classes)


    
@app.route('/find_similar_prob', methods=['POST','GET'])
def find_similar_prob():
    if "cheda" in request.form:
        prob= request.form['probleminput']
        print(prob)
        #do the code
        #problemna="ena fya tbi3a kn nahki nouja3 l3alem"
        #reponsetna="yomken enti 3lya b3ida nestana fik w dhaya3"
        openmodalsimilar = True
        teacher = Teacher.query.get_or_404(teacher_id_global)
        a= url_for('static', filename=teacher.image_path)
        results=KTC.query.filter_by(idTeacher=teacher_id_global).with_entities(KTC.idClasse).distinct().all()
        idclasses=[result[0] for result in results]
        classes=[]
        for i in idclasses:
            classes.append(Classe.query.filter_by(id=i).first())
        problems=[problem.Problem for problem in Problem.query.all()]
        print(problems)
        problemna=similar(prob,problems)[0]
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        print(problemna)
        yaya=Problem.query.filter_by(Problem=problemna).first()
        reponsetna=yaya.Reponse
        return render_template('baseTeacher.html',openmodalsimilar=openmodalsimilar,teacher_path=a,classes=classes,problemna=problemna,reponsetna=reponsetna,prob=prob)


    
@app.route('/delete_prob/<int:prob_id>', methods=['POST'])
def delete_prob(prob_id):
    prob = Portfolio.query.get_or_404(prob_id)
    prob.situation="done"
    db.session.commit()
    #tp = TP.query.filter_by(idProb=prob_id).first()
    #db.session.delete(tp)
    #db.session.commit()
    teacher = Teacher.query.get_or_404(teacher_id_global)
    a= url_for('static', filename=teacher.image_path)
    results=KTC.query.filter_by(idTeacher=teacher_id_global).with_entities(KTC.idClasse).distinct().all()
    print(results)
    idclasses=[result[0] for result in results]
    classes=[]
    for i in idclasses:
        classes.append(Classe.query.filter_by(id=i).first())
    sout=TP.query.filter_by(idTeacher=teacher_id_global).with_entities(TP.idProb).distinct().all()
    idProb=[sou[0] for sou in sout]
    probs=[]
    for i in idProb:
        p=Portfolio.query.filter_by(id=i).first()
        if p is not None:
            if p.situation=="still":
                probs.append(p)
    return render_template('Portfolio.html',teacher_path=a,probs=probs,classes=classes)



@app.route('/get_Response', methods=['GET', 'POST'])
def get_Response():
    global njoum_global
    if "ijeba" in request.form:
        #prob= request.form['Problem']
        responsekid1 = request.form['Response']
        my_list=re.split(r"\n|\r|=", responsekid1)
        responsekid=[element for element in my_list if element != '']
        prob=Portfolio.query.filter_by(Problem=njoum_global).first()
        score=score_reponse(eval(prob.Reponse),responsekid)
        print('bbbbbbbbbbbbbbbbbbb')
        print(score)


        krp=KRP(kid_id_global,prob.id,score)
        db.session.add(krp)
        db.session.commit()
        krps=KRP.query.filter_by(idKid=kid_id_global).all()
        print(len(krps))
        teslek=0.0
        for krp in krps:
            print('aaaaaaa')
            print(type(krp.score))
            print(krp.score)
            print('bbbbbbb')
            print(type(teslek))
            print(teslek)
            teslek=teslek+krp.score
        s=teslek/len(krps)
        kid=Kid.query.filter_by(id=kid_id_global).first()   
        kid.score=s
        db.session.commit()   
        if score==1:
            openmodalkid=1
        elif score >=0.5:
            openmodalkid=3
        else:
            openmodalkid=2
        
        return render_template('/interface_kid.html',open_modalkid=openmodalkid)
    if "nass" in request.form:
        prob=Portfolio.query.filter_by(situation="now").first()
        njoum_global=prob.Problem
        language = 'en'
        tts = gTTS(text=njoum_global, lang=language)
        tts.save("static/sound/sout.mp3")
        return render_template('/interface_kid.html',problem=prob.Problem,smakdouwn="static/sound/sout.mp3")

@app.route('/recuperer', methods=['POST'])
def recuperer():
    text = request.form['my_prob']
    print("Le texte soumis est : ", text)
    prob=Portfolio.query.filter_by(Problem=text).first()
    global tsawerpath_global
    if prob is None:
        images = ['static/images/Prob/prob1.png',
                  'static/images/Prob/prob2.png',
                  'static/images/Prob/prob3.png',
                  'static/images/Prob/prob4.png',
                  'static/images/Prob/prob5.png',
                  'static/images/Prob/prob6.png',
                  'static/images/Prob/prob7.png',
                  'static/images/Prob/prob8.png']
        tsawerpath_global=images
        return render_template('generation2.html', images=images)
    else:
        prob.situation="now"
        db.session.commit()
        tsawerpath_global=my_function(text)
        print(tsawerpath_global)
        scheduler.add_job(set_done, 'date', run_date=datetime.now() + timedelta(minutes=5), args=[prob.id])
        return render_template('generation2.html', images=tsawerpath_global)

def set_done(prob_id):
    with app.app_context():
        prob=Portfolio.query.filter_by(id=prob_id).first()
        prob.situation="done"
        db.session.commit()
    print("done")



@app.route('/reaction3')
def reaction3():
    return render_template('reaction2.html')


@app.route('/add_image', methods=['POST'])
def add_image():
    if "zidsawer" in request.form:
        add_image = request.form['add-image']
        yesta3ml=add_image+" clipart"
        print(yesta3ml)
        image=txt2Im(yesta3ml)
        sourci = 'static/images/Prob/image_added.png'
        image.save(sourci)
        l=tsawerpath_global
        l.append(sourci)
        return render_template('generation2.html', images=l)





if __name__ == '__main__':

    app.run()

