import os
from flask import Flask, request
from flask import render_template,redirect,url_for
from flask import flash, make_response
from logging.handlers import RotatingFileHandler
import pymysql
import logging
app=Flask(__name__)
app.secret_key = 'ss'


@app.route('/login')
@app.route('/',methods=['GET','POST'])
def index():



    if request.cookies.get('username') !=None:
        app.logger.warning(f'LOGIN:{request.cookies.get("username")} has logged in successfully.')
        return render_template('page.html',user=request.cookies.get('username'))


    cred={'suhail':'pass','ss':'aa'}
    if request.method=='POST':
        if cred.get(request.form['username'])==None:
            flash("Error")
            app.logger.warning('ERROR:No user name was found')
            return 'Error,no user found'


        elif cred.get(request.form['username']) != None and cred.get(request.form['username'])==request.form['password']:
            response=make_response(redirect(url_for('index')))
            response.set_cookie('username',request.form['username'])
            return response
            #render_template('login.html',req_type=request.method,username=request.form['username'])
        else:
            return (f'<h1>Sorry,{request.form["username"]}.<p>Wrong password.</p></h1>')
    elif request.method=='GET':
        app.logger.warning('INFO:new GET request')
        return render_template('login.html',req_type=request.method)

@app.route('/logout')
def logout():
    response=make_response(redirect(url_for('index')))
    response.set_cookie('username','',expires=0)
    return response

@app.route('/user/<username>')
def hello_world(username):

    return 'Suhail '+str(username)
@app.route('/')
def page(user=None):
    user=request.cookies.get('username')

    if user!="":
        return render_template('page.html', user=user)
    else:
        return redirect(url_for('index'))


def valid(username,password):

    if valid:
        return True
    else:
        return Flase


if __name__=='__main__':

    host=os.getenv('IP','0.0.0.0')
    port= int(os.getenv('PORT',8085))
    app.debug=True
    app.secret_key = 'ss'


    #logging


    handler=RotatingFileHandler('error1.log',maxBytes=100000,backupCount=4)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host=host,port=port)
