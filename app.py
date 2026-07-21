from flask import Flask,session , render_template,redirect,url_for,flash,request
from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from tmdb import search_movie
from dotenv import load_dotenv
import os
load_dotenv()

app=Flask(__name__)
bcrypt = Bcrypt(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.sqlite3"
db=SQLAlchemy(app)
app.secret_key=os.getenv("SECRET_KEY")
class Users(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),unique=True,nullable=False)
    hashed_password=db.Column(db.String(200),nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    movies = db.relationship('Movies', backref='user', lazy=True,cascade = 'all,delete-orphan')

    def __init__(self,name,hashed_password):
        self.name = name
        self.hashed_password = hashed_password

class Movies(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100) ,nullable=False)
    rating = db.Column(db.Double)
    poster=db.Column(db.String)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    watched = db.Column(db.Boolean,default = False)
    release_date = db.Column(db.String(50))


@app.route("/home")
@app.route("/")
def home():
    return render_template("home_page.html")
@app.route("/user")
def user():
    if "user" in session:
        name = session["user"]
        current_user = Users.query.filter_by(name=name).first()
        return render_template("user_page.html",user = current_user)
    else:
        flash("Please login!!" , 'error')
        return redirect(url_for('login'))    
    
@app.route("/add",methods=["GET","POST"])
def add():
    if request.method=="POST":
        user = session["user"]
        flag = False
        movie_name = request.form["movie"]
        watched = request.form["adder"]
        found_user = Users.query.filter_by(name=user).first()
        if(watched=="YES"):
            flag = True
        movie_data=search_movie(movie_name)
        if movie_data:
            movie = Movies(title = movie_data['title'],watched = flag,rating = movie_data['rating'],
                       poster=movie_data['poster'],release_date=movie_data['release_date'])
        else:
            movie=Movies(title=movie_name , watched=flag);
        found_user.movies.append(movie)
        db.session.commit()
        return redirect(url_for("user"))
    else:
        return render_template("add_movie.html")
   
@app.route("/delete" , methods = ["GET","POST"])
def delete():
    if request.method=="POST":
        movie_name = request.form["delete"].strip()
        user = session["user"]
        found_user = Users.query.filter_by(name=user).first()
        ref_id = found_user.id
        movie = Movies.query.filter_by(title=movie_name, user_id=ref_id).first()
        if not movie:
            flash("Enter Valid Movie","info")
            return redirect(url_for("user"))
        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for("user"))
    else:
        return render_template("delete_movie.html")

@app.route("/login" , methods = ["GET","POST"])
def login():
    if request.method=='POST':
        user = request.form['nm']
        password = request.form["password"]
        session["user"] = user
        existing_user = Users.query.filter_by(name=user).first()
        if existing_user:
            flash("Username Already taken : " , "error")
            session.pop("user",None)
            return redirect(url_for("login"))
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        sample1 = Users(name=user,hashed_password=hashed_pw)
        db.session.add(sample1)
        db.session.commit()
        return redirect(url_for("user"))
    else:
        if "user" in session:
            user = session["user"]
            flash("you are already logged in ","info")
            return redirect(url_for("user"))
        else:
            return render_template("login.html")

@app.route("/enter" , methods =["GET","POST"])
def enter():
    if request.method=="POST":
        user = request.form["nm"]
        password=request.form["password"]
        session["user"] = user
        existing_user=Users.query.filter_by(name=user).first()
        if existing_user:
            if bcrypt.check_password_hash(existing_user.hashed_password,password):
                return redirect(url_for("user"))
            else:
                flash("Enter Valid Password","error")
                return render_template("login.html")
        else:
            flash("Enter Valid Username" , "error")
            return render_template("login.html")
    else:
        if "user" in session:
            flash("U are Already logged in!!" , "error")
            return redirect(url_for("user"))
        return render_template("login.html")
@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user",None)
        flash("you logged out","info")
    else:
        flash("You weren't logged in at first place","error")
    return redirect(url_for("login"))

@app.route("/deleteuser" , methods=["GET"])
def popper():
    user = session["user"]
    found_user = Users.query.filter_by(name=user).first()
    session.pop("user",None)
    flash("USER DELETED" , "info")
    db.session.delete(found_user)
    db.session.commit()
    return redirect(url_for("login"))

@app.route("/admin",methods=["GET","POST"])
def admin():
    if request.method=="POST":
      pwd=request.form['pwd']
      if pwd==os.getenv("ADMIN_PASSWORD"):
        val = Users.query.all()
        return render_template("database.html" , users=val)
      else:
        flash("Incorrect password" , "error")
        return render_template("security.html")
    else:
        return render_template("security.html")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)