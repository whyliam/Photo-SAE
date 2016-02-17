# coding=utf-8
#from __future__ import with_statement


import os
import sys
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, send_from_directory
import json
import time
# configuration

import sae.const

from models import Posts, Users, Photos, Upload
from setting import *
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.before_request
def load_web():
    g.title = 'Why · Liam · Photo '
    g.userid = session.get('userid')


@app.route('/')
@app.route('/page=<int:page>')
def index(page=1):
    mess = Posts.get_news_by_page(page)
    pageCount = Posts.get_per_count()
    pageurl = "/page="
    return render_template('Home/index.html', msgs=mess, currentPage=page, pageCount=pageCount,pageurl=pageurl)

@app.template_filter('sdata')
def format_datetime(s):
    return s.strftime('%Y/%m')

# @app.route('/search?keyword=<q>')
# @app.route('/search?keyword=<q>/page=<int:page>')
# def search(q,page=1):
@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/page=<int:page>', methods=['GET', 'POST'])
def search(page=1):
    q = request.args['keyword'].split('/page')[0]
    ids = Posts.search_keyword(q)
    print ids
    if ids:
        mess = Posts.search_news_by_page(page,ids)
        pageCount = Posts.get_per_count(len(ids))
        pageurl = "/search?keyword="+q+"/page="
        return render_template('Home/index.html', msgs=mess, currentPage=page, pageCount=pageCount,pageurl=pageurl)
    else:
        id = 0
        mess = Posts.get_a_post(id)
        pageurl = "/search?keyword="+q+"/page="
        return render_template('Home/index.html', msgs=mess, currentPage=1, pageCount=1,pageurl=pageurl)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        msg = Users.login(name, password)
        if (msg['state'] == 'successed'):
            session['userid'] = msg['id']
            session['logged_in'] = True
            session['username'] = name
            return redirect(url_for('newpost'))
        else:
            flash(msg['message'])
            error = msg['message']
    return render_template('Login/index.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    userid = session.get('userid')
    rannew = time.time()
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        local = request.form['local']
        tags = request.form['tags']
        rannew = request.form['rannew']
        content = request.form['content']
        Posts.add_a_post(title, date, local, tags, content, userid, rannew)
        return redirect(url_for('index'))
    return render_template('New/index.html', rannew=rannew)


@app.route('/uploadimg', methods=['GET', 'POST'])
def uploadimg(x_s=0, y_s=0):
    if request.method == 'POST':
        userid = session.get('userid')
        x_s = request.form['x_s']
        y_s = request.form['y_s']
        rannew = request.form['rannew']
        hero = request.form['hero']
        photo = request.files['heroupload']
        alt = ''
        if photo:
            img_x_y = Upload.img_x_y(photo)
            href = Upload.upload_image(photo, '_o_', 0, 800)
            src = Upload.upload_image(photo, '_s_', x_s, y_s)
            Photos.add_a_photo(href, src, alt, img_x_y * hero, userid, rannew)

            return json.dumps({'error': 0, 'url': src})
        else:
            flash('请上传正确的照片')
            return json.dumps({'error': 1, 'info': '请上传正确的照片'})
    return render_template("uploadimg.html")


@app.route('/<int:y>/<int:m>/<k>')
def paper(y, m, k):
    mess = Posts.get_a_post(k)
    return render_template('Paper/index.html',mess=mess)
