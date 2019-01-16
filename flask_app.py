import os
import os.path
from flask import Flask, request
from flask import render_template,redirect,url_for
from flask import flash, make_response
from logging.handlers import RotatingFileHandler
import pymysql
import logging
import pathlib
import glob


UPLOAD_FOLDER = '/home/suhail09s/mysite/static/profile'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.secret_key = 'ss'
def connect():
    global dbHost,dbUser,dbPassword,cursor,dbName,conn,serverStatus
    serverStatus='Not connected'
    dbHost=os.getenv('IP','0.0.0.0')
    dbUser='suhail09s'
    dbPassword='passme111'
    dbName='suhail09s$flask'
    conn=pymysql.connect(host='suhail09s.mysql.pythonanywhere-services.com',user=dbUser,password=dbPassword,db=dbName)
    cursor=conn.cursor()
    serverStatus='Connected'
    forceDB()
    return serverStatus

@app.route('/decache',methods=['GET','POST'])
def decache():
    response=make_response(redirect('/listall'))
    response.set_cookie('username',request.form['username'])
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
#@app.after_request

def set_response_headers(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

@app.route('/closeconn')
def closeConn():
    conn.commit()
    cursor.close()
    return redirect(url_for('index'))

@app.route('/login')
@app.route('/',methods=['GET','POST'])
def index():

    try:
        connect()
    except:
        return 'Error connecting to SQL server'

    if request.cookies.get('username') !=None:
        app.logger.warning(f'LOGIN:{request.cookies.get("username")} has logged in successfully.')
        return render_template('page.html',user=request.cookies.get('username'),serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')))


    if request.method=='POST':
        if (len(request.form['username']))==0: # No user name wes provided
            flash("Error: No username name was provided")
            app.logger.warning('ERROR:No user name was provided')
            return redirect('/')
            #render_template('page.html',req_type=request.method,serverStatus=serverStatus,user=request.form['username'],profile=getProfilePic(request.cookies.get('username')))

        elif valid(request.form['username'],request.form['password'])== True:
            response=make_response(redirect(url_for('index')))
            response.set_cookie('username',request.form['username'])
            return response

        else:
            flash('Error:incorrect username or password.')
            return redirect('/')
            #render_template('page.html',req_type=request.method,user="WRONG",serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')))
    elif request.method=='GET':
        app.logger.warning('INFO:new GET request')
        return render_template('login.html',user='WRONG',req_type=request.method,serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')))

@app.route('/logout')
def logout():
    try:
        closeConn()
    except:
        pass
    response=make_response(redirect(url_for('index')))
    response.set_cookie('username','',expires=0)
    return response
@app.route('/forcedb')
def forceDB():
    #set defult profile photo
    defultPic='static/profile/defult.png'
    cursor.execute(f"update user set url='{defultPic}' where url is NULL ")
    conn.commit()

@app.route('/')
def page(user=None):
    user=request.cookies.get('username')

    if user!="":
        return render_template('page.html', user=user,serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')))
    else:
        return redirect(url_for('index'))
@app.route('/sql')
def consql():
    flash('Connected to DB server')


def valid(username="",password="",checkNewEntry=False):
    #MYSQL COMMAND

    app.logger.warning(f'LOGIN:Attempt - username({username}) and password({password})')
    cursor.execute(f"SELECT * FROM user where (username='{username}' and password='{password}')")
    res=cursor.fetchone()
    app.logger.warning(f'LOGIN:Found -{res}')

    if res==None: # no user was found
        return False
    elif res[1]==username and res[2]==password: #valid login
        return True
    elif res[1]==username and res[2]!=password:#wrong password
        return False
    else:
        return False
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.cookies.get('username')==None:
         flash('you need to login first.')
         return redirect('/')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            profile_pic=str(request.cookies.get('username'))+'.pic'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic))
            flash('successfully uploaded profile picture')
            Ur=getProfilePic(request.cookies.get('username'))
            cursor.execute(f"update user set url='{Ur}' where username='{request.cookies.get('username')}'")
            conn.commit()
            return redirect((url_for('index')))

    return render_template('upload.html',serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')))

@app.route('/selected',methods=['GET','POST'])
def selected():
    if request.cookies.get('username')==None:
         return redirect('/')
    if request.form['submit']=='remove'  :
        for b in request.form.getlist('box'):
            sqlString=(f"select username FROM user WHERE user_id = '{b}' ")
            cursor.execute(sqlString)
            Us=cursor.fetchone() #fetch username that correspond with user_id to be removed.
            try:
                os.remove(f'mysite/static/profile/{Us[0]}.pic')
            except:
                flash(f"{Us[0]}'s picture wasn't deleted or wasn't setup. ")
            sqlString=(f"DELETE FROM user WHERE user_id = '{b}' ")
            cursor.execute(sqlString)
            flash(f'succsessfully removed user :{Us[0]}')
        conn.commit()
    elif request.form['submit']=='update' and len(request.form.getlist('box'))==1:
        user_id=(request.form.getlist('box'))[0]
        cursor.execute(f"SELECT * FROM user where (user_id='{user_id}')")
        res=cursor.fetchone()
        update(res)
        return redirect(request.url)
    return redirect(url_for('listAll'))


@app.route('/listall',methods=['GET','POST'])
def listAll():
    if request.cookies.get('username')==None:
         return redirect('/')
    else:
        connect()
        cursor.execute("SELECT * FROM user")
        res=cursor.fetchall()
        return render_template('list.html', res=res,serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')))



@app.route('/newentry',methods=['GET','POST'])
def newEntry():


        connect()
        if request.cookies.get('username') ==None:
            return "Failed, You need to login first. \n<a href='/'>Login page</a>"

        elif request.method=='GET':
            return render_template('new.html',serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')))
        elif request.method=='POST':
            Us=request.form['username']
            Ps=request.form['password']
            Cr=request.cookies.get('username')
            try:
                Pi=request.files['file']
            except:
                Pi=None

            if (Us=='' or Ps==''):
                flash('Please enter a valid username and password')
                return render_template('new.html',serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')))
            cursor.execute(f"SELECT * FROM user where (username='{Us}')")
            if (cursor.fetchone())==None: # checks if username is already exists.

                cursor.execute(f"INSERT INTO user (username,password,creator) VALUES ('{Us}','{Ps}','{Cr}')")
                conn.commit()

                if Pi==None:
                    flash('successfully inserted, do not forget to upload a profile pic')
                    return redirect(url_for('newEntry'))
                if Pi !=None:
                    if Pi and allowed_file(Pi.filename):

                        profile_pic=str(request.form['username'])+'.pic'
                        Pi.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic))
                        flash("successfully inserted, nice avatar.")
                        Ur=getProfilePic(request.form['username'])
                        cursor.execute(f"update user set url='{Ur}' where username='{request.form['username']}'")
                        conn.commit()
                        return redirect(url_for('newEntry'))
            else:
                flash (f'{Us} is already exists')
                return render_template('new.html',serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')))
        else:
            return '<h5>Error,user aleady exist or sql syntax eror</h5>'


@app.route('/update',methods=['GET','POST'])
def update(res=None):
    connect()
    if request.cookies.get('username') ==None:
        return redirect('/')
    if request.method=='GET':
        cursor.execute(f"select * from user where username='{request.cookies.get('username')}'")
        res=cursor.fetchone()
        app.logger.warning('GET req and after fetch from sql and about to render')
        return render_template('update.html',req_type=request.method,serverStatus=serverStatus,profile=getProfilePic(request.cookies.get('username')),res=res)
    if request.method=='POST' and res==None:
        app.logger.warning('POST request')
        user_id=request.form['user_id']
        Us=request.form['username']
        Ps=request.form['password']
    if request.method=='POST' and res!=None:
        app.logger.warning(f'POST reques with res={res}')
        try:
            user_id=res[0]
            Us=res[1]
            Ps=res[2]
        except:
            app.logger.warning(f'manybe post or no res ')
        #Pi=res[4]
        if Us=='' or Ps=='':
            flash("can't leave them empty.")
            return ('good')
        try:
            Pi=request.files['file']
        except:
            Pi=None
        if Pi==None:
            cursor.execute(f"select * from user where user_id='{user_id}'")
            res=cursor.fetchone()
            app.logger.warning(f'just before rendering update page with res values fetched from sql-res={res}')
            cursor.execute(f"update user set username='{Us}',password='{Ps}' where user_id='{user_id}'")
            app.logger.warning(f'about to commit it-res={res}')
            conn.commit()
            return redirect(url_for('listAll'))

        if Pi !=None:
            if Pi and allowed_file(Pi.filename):

                profile_pic=str(res[1])+'.pic'
                Pi.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic))
                flash("successfully inserted, nice avatar.")
                Ur=getProfilePic(request.form['username'])
                cursor.execute(f"update user set username='{Us}', password='{Ps}', url='{Ur}' where user_id='{user_id}'")
                conn.commit()
                return redirect(url_for('listAll'))
    return ('v')



def getProfilePic(username):
    profile=""
    username=str(username)
    globpath=(f'mysite/static/profile/{username}.pic')
    for pic in (glob.glob(globpath, recursive=True)):
        profile=pic


    path='static/profile/'+str(profile).split('/')[-1]
    checkPath=pathlib.Path('mysite/'+path)
    defult='static/profile/defult.png'

    if checkPath.is_file()==True:


        return path
    else:
        return defult

if __name__=='__main__':

    host=os.getenv('IP','0.0.0.0')
    port= int(os.getenv('PORT',8085))
    app.debug=True
    app.secret_key = 'ss'
    flash('init page')
    consql()

    #logging


    handler=RotatingFileHandler('error1.log',maxBytes=100000,backupCount=4)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host=host,port=port)

