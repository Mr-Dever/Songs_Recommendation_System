from flask import Flask, render_template, redirect, request, session ,url_for
from flask_session import Session
import pyrebase 
import pickle
from werkzeug.utils import redirect
import Recommenders as Recommenders
import random
from firebase_admin import auth 
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("Account_key.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)
app.secret_key = "vdqafuagwgfsflahipj-28e028234273237r2}@?FD!!:}hyfu72177#$#%@*8705*667[1-9e107e11oe1t1inkci"
firebaseConfig = {
  'apiKey': "AIzaSyCeR0ieO38mB0x-gx82u1BIncNlV_uM-p4",
  'authDomain': "song-36efe.firebaseapp.com",
  'projectId': "song-36efe",
  'databaseURL':"https://song-36efe-default-rtdb.europe-west1.firebasedatabase.app/",
  'storageBucket': "song-36efe.appspot.com",
  'messagingSenderId': "474681232531",
  'appId': "1:474681232531:web:53b3dbbbedceca677cd166",
  'measurementId': "G-EHTKJ7NQXC"
}
firebase = pyrebase.initialize_app(firebaseConfig)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = firebase.database()
Authe = firebase.auth()
# to un zip the pickle file to use the dataset in our program
train = pickle.load(open('trainset.pkl','rb'))
# from Recommenders we need to import similarity_recommender() class so that we use our all usefull functions
is_model = Recommenders.similarity_recommender()
# in this line of code we give the argument to the function named create_s() in which our program can create similarities
is_model.create_s(train , 'user_id' , 'song')
u = train['user_id'].unique()
# @app.route("/")
# def index():
#     return render_template("index.html")

# //////////////////////////////////////
# Login and Signup Function Goes Here
# //////////////////////////////////////
@app.route('/signup')
def Signup_page():
    return render_template("signup.html")
@app.route('/register' , methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and len(dict(request.form)) > 0:
      userdata = dict(request.form)
      session['username'] = userdata['username']
      session['email'] = userdata["email_address"]
      session['password'] = userdata["password"]
      if session['username'] == "" or session['username'] == None:
        username_error = "Name can't be blank"
        return render_template("signup.html", user_error = username_error)
      elif not session['password'] or len(session['password'])  < 6 :
        password_error = "Password Must be Atleast 6 characters Long"
        return render_template("signup.html", password_error = password_error)
      elif not session['email'] or '@' not in session['email'] or '.' not in session['email'] :
        email_error = "Invalid Email"
        return render_template("signup.html", email_error = email_error)
      else:
        user = Authe.create_user_with_email_and_password(session['email'] , session['password'])
        new_user = auth.get_user_by_email(session['email'])
        username_get = db.child(new_user.uid).child("username").push(session['username'])
        email_get = db.child(new_user.uid).child("Email").push(session['email'])
        id = db.child(new_user.uid).child("ID").push(new_user.uid)
        return redirect(url_for('recommend'))
    else:
      return "sorry Something went wrong try again"
# //////////////////////////////////////
# Login Function
# //////////////////////////////////////
@app.route('/login_page')
def Login_page():
    return render_template("login.html")
@app.route('/login_user' , methods=['GET', 'POST'])    
def Login():
    if request.method == 'POST' and len(dict(request.form)) > 0:
        userdata = dict(request.form)
        session['email'] = userdata["email"]
        session['password'] = userdata["password"]
        if session['email'] == "" or '@' not in session['email'] or '.' not in session['email'] :
          email_error = "Invalid Email!"
          return render_template("login.html", email_error = email_error)
        elif len(session['password']) >= 6:
          user = Authe.sign_in_with_email_and_password(session['email'] , session['password'])
          return redirect(url_for('recommend'))
        else:
          password_error = "Wrong Password"
          return render_template("login.html", password_error = password_error)
    else:
        return redirect(url_for('Login_page'))
# //////////////////////////////////////
# Logout Function
# //////////////////////////////////////
@app.route('/logout')
def Logout():
  session['email'] = None
  return redirect(url_for('Login_page'))
# //////////////////////////////////////
# Login and Signup Function End Here
# //////////////////////////////////////
# //////////////////////////////////////
# Refresh recommendations Function Goes Here
# //////////////////////////////////////
@app.route('/refresh' , methods = ['GET' , 'POST'])
def refresh():
      # now we have songs and there link in same column and both are merged so we need to seperate them to get the values
      # i can do it with slicing and store the values in below saparate lis
      songlink_refresh =[]
      song_refresh = []
      # Function for seperate songs name and links
      seperate_song_link_refresh(songlink_refresh , song_refresh)
      # to get the newer recommendation we need random values to recommend user the different songs
      # so that we choose set() function because we don't want any duplicate number and also not any user want duplicate  songs
      a=set()
      # to done above procedure agian we need to run a loop that generate 10 random numbers to get the newer  recommendations
      for i in range(0,10):
          # we get and add the random values in out set() named (" a ")
          a.add(random.randint(0,1000))
      songlink_ = []
      song_ = []
      for i , v in enumerate(a):
        songlink_.append(songlink_refresh[v])
        song_.append(song_refresh[v])

      return render_template('refresh.html' , songlink_refresh = songlink_  ,  song_refresh = song_)

# //////////////////////////////////////
# Refresh recommendations Function End Here
# //////////////////////////////////////

# //////////////////////////////////////
# Function for seperate songs name and links for refresh recommendations Goes Here
# //////////////////////////////////////
def seperate_song_link_refresh(songlink_refresh , song_refresh):
    # now we have songs and there link in same column and both are merged so we need to seperate them to get the values
    # i can do it with slicing and store the values in below saparate lists 
    # now we need a loop to done above work 
    # to solve our problem we are using for loop so :
    # first we run our loop 1500 times so that 1500 our loop get 1500 songs from the dataset
    for i in range(0,1501):
        # now we use try and except because if our program got any error to execute any line of dataset we ignore that  line so we get the valid values
        try:
          tr = train['song'][i]
        # before below line we have the value in our datatset is ( Song For You - Alexi Murdoch - https://www.youtube.  com/watch?v=HeHiio1sTTI)
          song_link = tr[-43:]
        # after the above line now we have ( https://www.youtube.com/watch?v=HeHiio1sTTI ) separated from mergerd column
        # and after these we need to append it and on below line we append it in our list named (" songlink_refresh ")
          songlink_refresh.append(song_link)
        except:
          continue
        try:
          tr = train['song'][i]
        # before below line we have the value in our datatset is ( Song For You - Alexi Murdoch - https://www.youtube.  com/watch?v=HeHiio1sTTI)
          song = tr[:-46]
        # after the above line now we have ( Song For You - Alexi Murdoch ) separated from mergerd column
        # and after these we need to append it and on below line we are going to append it in out list named (" song ")
          song_refresh.append(song)
        except:
          continue
# //////////////////////////////////////
# Function for seperate songs name and links End Here
# //////////////////////////////////////


# //////////////////////////////////////
# Function1500 random Numbers End Here
# //////////////////////////////////////
def seperate_song_link_recommendation(songlink,song,recommendation): 
    # now we need a loop to done above work 
    # to solve our problem we are using for loop so :
    # we use for loop to perform our task that is to again separate the song name and song link but this time we    separate them from the recommendations that recommended by our program
    for i in recommendation['song']:
        # before below line we have the value in our datatset is ( Song For You - Alexi Murdoch - https://www.  youtube.com/watch?v=HeHiio1sTTI)
        song_link = i[-43:]
        # after the above line now we have ( https://www.youtube.com/watch?v=HeHiio1sTTI ) separated from mergerd   column
        # and after these we need to append it and on below line we append it in our list named (" song_link ")
        songlink.append(song_link)
        # before below line we have the value in our datatset is ( Song For You - Alexi Murdoch - https://www.  youtube.com/watch?v=HeHiio1sTTI)
        songname = i[:-46]
        # after the above line now we have ( Song For You - Alexi Murdoch ) separated from mergerd column
        # and after these we need to append it and on below line we append it in our list named (" song ")
        song.append(songname)
# //////////////////////////////////////
# Function1500 random Numbers End Here
# //////////////////////////////////////

# //////////////////////////////////////
# Favourite Songs Function Goes Here
# //////////////////////////////////////
@app.route("/favourite_page")
def Favourite_page():
  user = auth.get_user_by_email(session['email'])
  favsongs = db.child(user.uid).child('Fav-Songs').get().val()
  fav_songs = []
  if favsongs is not None:
    favsong = db.child(user.uid).child('Fav-Songs').get()
    for song in reversed(favsong.each()):
        songlist = song.val()
        fav_songs.append(songlist)
  
  fav_songs_name = []
  fav_songs_link = []
  for i in fav_songs:
    if "https" in i:
      # k = k + 2
      fav_songs_link.append(i)
    elif "https" not in i:
      # j = j + 1
      fav_songs_name.append(i)

  favourite = zip(fav_songs_name , fav_songs_link)
  return render_template("favourite.html" , favourite = favourite)

@app.route("/favourite" , methods = ['GET','POST'])
def Favourite():
    if request.method == 'POST' and len(dict(request.form)) > 0:
      userdata = dict(request.form)
      songss = userdata["song"]
      songlink = userdata["songlink"]
      user = auth.get_user_by_email(session['email'])
      db.child(user.uid).child('Fav-Songs').push(songss)
      db.child(user.uid).child('Fav-Songs').push(songlink)
      return redirect(url_for("recommend"))
    else:
      return render_template('favourite.hmtl')
# //////////////////////////////////////
# Favourite Songs Function end Here
# //////////////////////////////////////
# //////////////////////////////////////
# Delete Favourite Songs Function end Here
# //////////////////////////////////////
@app.route('/delete_fav/<int:id>')
def Delete(id):
  user = auth.get_user_by_email(session['email'])
  db.child(user.uid).child('Fav-Songs').remove()
  return redirect(url_for("Favourite_page"))
# //////////////////////////////////////
# Delete Favourite Songs Function end Here
# //////////////////////////////////////
# //////////////////////////////////////
# Main Function Goes Here
# //////////////////////////////////////
@app.route('/')
def recommend():  
  if not session.get('email'):
    return redirect(url_for('Login_page'))
  else:
    
    # to assign a variable to get the specifis unique user data and Print the songs for that user
    user_id1 = u[0]
    # in this line we give the argument in the form of user id means it Recommend songs for the user using personalized     model
    recommendation = is_model.recommend_s(user_id1)
    # now we have songs and there link in same column and both are merged so we need to seperate them to get the    values
    # i can do it with slicing and store the values in below saparate lists 
    # 1st one is for songs link
    songlink = []
    # and 2nd one is for Songs Names
    song = []
    seperate_song_link_recommendation(songlink,song,recommendation)
    return render_template("home.html",songlink = songlink , song = song)

# //////////////////////////////////////
# Main Function End Here
# //////////////////////////////////////


if __name__ == '__main__':
    app.run()