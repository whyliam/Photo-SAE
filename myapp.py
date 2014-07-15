# coding=utf-8
#from __future__ import with_statement


import os
import sys
import json
import time
import random
import datetime
import MySQLdb
from PIL import Image
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, send_from_directory
from werkzeug import secure_filename

import pinyin
import StringIO


# configuration
ALLOWED_EXTENSIONS = set(['png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG'])
DEBUG = True
SECRET_KEY = 'development key'
PASSWORD = 'default'
POSTS_PER_PAGE = 3

import sae.const


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return MySQLdb.connect(
        sae.const.MYSQL_HOST, sae.const.MYSQL_USER, sae.const.MYSQL_PASS,
        sae.const.MYSQL_DB, port=int(sae.const.MYSQL_PORT), charset='utf8')


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
@app.route('/page=<int:page>')
def index(page=1):
    page = page - 1
    c = g.db.cursor()
    c.execute(
        'SELECT count(`id`) FROM `naaln_blog`')
    count = list(c.fetchall())[0][0]
    count = count if count else 1
    pageCount = (count - 1) / POSTS_PER_PAGE + 1
    c.execute(
        'SELECT `id`, `title`, `subname`, `article`, `color`, `time`, `location`, `content`, `tags` FROM naaln_blog ORDER BY `time` DESC LIMIT %s,%s' % (page * POSTS_PER_PAGE, POSTS_PER_PAGE))
    msgs = list(c.fetchall())
    blogs = []
    for id, title, subname, article, color, time, location, content, tags in msgs:
        c.execute(
            'SELECT `photo_id` FROM `naaln_hero` WHERE `blog_id` = %s' % id)
        hero = list(c.fetchall())[0][0]
        c.execute(
            'select href, src, alt from naaln_photo where blog_id =%s and id !=%s' %
            (id, hero))
        photos = list(c.fetchall())
        c.execute(
            'select href, src, alt from naaln_photo where id = %s' % hero)
        pictures = list(c.fetchall())
        blog = [id, title, subname, article, color, hero,
                time, location, content, photos, pictures]
        blogs.append(blog)
    mess = tuple(blogs)

    return render_template('Home/index.html', msgs=mess, currentPage=page + 1, pageCount=pageCount)


@app.route('/search/<q>')
def search(q):
    c = g.db.cursor()
    sql = """(select id, title, article, color, time, location, content from naaln_blog  WHERE `title` LIKE %s ORDER BY `time` DESC ) \
        union (select id, title, article, color, time, location, content from naaln_blog  WHERE 
            `content` LIKE %s ORDER BY `time` DESC) """
    c.execute(sql, (('%' + q + '%', '%' + q + '%',)))
    msgs = list(c.fetchall())
    print sql
    print msgs
    blogs = []
    for id, title, article, color, time, location, content in msgs:
        c.execute(
            'SELECT `photo_id` FROM `naaln_hero` WHERE `blog_id` = %s' % id)
        hero = list(c.fetchall())[0][0]
        c.execute(
            'select href, src, alt from naaln_photo where blog_id =%s and id !=%s' %
            (id, hero))
        photos = list(c.fetchall())
        c.execute(
            'select href, src, alt from naaln_photo where id = %s' % hero)
        pictures = list(c.fetchall())
        blog = [id, title, article, color, hero,
                time, location, content, photos, pictures]
        blogs.append(blog)

    return render_template('Home/index.html', msgs=tuple(blogs))


@app.route('/new')
def new():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    c = g.db.cursor()
    c.execute(
        'select id, title, article, color, time, location, content from naaln_blog')
    msgs = list(c.fetchall())
    return render_template('New/new.html', msgs=tuple(msgs))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        c = g.db.cursor()
        name = "'" + request.form['username'] + "'"
        password = request.form['password']
        c.execute(
            'select id, user, password from naaln_users where user =%s' % name)
        username = c.fetchall()
        if username:
            for id, user, psw in username:
                if password == psw:
                    session['logged_in'] = True
                    flash('You were logged in')
                    return redirect(url_for('new'))
                else:
                    error = 'Invalid password'
        else:
            error = 'Invalid username'
    return render_template('Login/login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def save_name(filename, size):
    ext = filename.rsplit('.', 1)[1]
    d = filename.rsplit('.', 1)[0]
    fn = time.strftime('%Y%m%d%H%M%S')
    fn = fn + '_%d' % random.randint(0, 100)
    # 重写合成文件名
    name = os.path.join(d + size + fn + "." + ext)
    return name


@app.route('/background', methods=['GET', 'POST'])
def upload_file():
    import sae.storage
    access_key = sae.const.ACCESS_KEY
    secret_key = sae.const.SECRET_KEY
    appname = sae.const.APP_NAME
    bucket = sae.storage.Bucket('picture')
    bucket.put()

    c = g.db.cursor()
    title = "'" + request.form['title'] + "'"
    article = "'" + request.form['article'] + "'"
    subname = request.form['sub-name']
    if len(subname) < 1:
        subname = ""
        length = len(title)
        for i in xrange(1, length - 1):
            print title[i]
            subname = subname + str(pinyin.convert(title[i]))
            if len(subname) > 10:
                break
    subname = "'" + subname + "'"
    color = random.choice(
        ('blue', 'brown', 'green', 'orange', 'pink', 'purple', 'yellow'))
    color = "'" + color + "'"
    time = "'" + request.form['time'] + "'"
    location = "'" + request.form['location'] + "'"
    content = "'" + request.form['content'] + "'"
    tags = "".join(request.form['tags'])
    tags.split(" ")
    tags = "'" + tags + "'"

    # tags = tuple(tags)

    hero = request.files['hero']
    uploaded_files = request.files.getlist("hero[]")

    info = (title, subname, article, color, time, location, content, tags)
    c.execute(
        'INSERT INTO `naaln_blog` (`title`, `subname`, `article`, `color`, `time`, `location`, `content`, `tags`) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s);' %
        info)
    g.db.commit()
    bid = c.lastrowid
    print bid

    if article == "'content portrait full'":
        x_s = 440
    elif article == "'content landscape'":
        x_s = 724
    elif article == "'content landscape full'":
        x_s = 724
    elif article == "'content landscape full blog'":
        x_s = 310
    else:
        x_s = 724

    print hero
    if hero and allowed_file(hero.filename):
        filename = secure_filename(hero.filename)
        im = Image.open(hero)
        o_image = save_name(filename, "_o_")
        output = StringIO.StringIO()
        im.save(output, 'JPEG')
        bucket.put_object(o_image, output.getvalue())
        output.close()
        href = "'" + bucket.generate_url(o_image) + "'"
        (x, y) = im.size  # read image size
        y_s = y * x_s / x  # calc height based on standard width
        # resize image with high-quality
        out = im.resize((x_s, y_s), Image.ANTIALIAS)
        s_image = save_name(filename, "_s_")
        output = StringIO.StringIO()
        out.save(output, 'JPEG')
        bucket.put_object(s_image, output.getvalue())
        output.close()
        src = "'" + bucket.generate_url(s_image) + "'"
        c.execute(
            'INSERT INTO `naaln_photo` (`id`, `blog_id`, `href`, `src`) VALUES (NULL, %s, %s, %s '');' %
            (bid, href, src))
        g.db.commit()
        pid = c.lastrowid
        c.execute(
            'INSERT INTO `naaln_hero` (`blog_id`, `photo_id`) VALUES (%s, %s)' %
            (bid, pid))
        g.db.commit()

    if uploaded_files:
        filenames = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                im = Image.open(file)
                o_image = save_name(filename, "_o_")
                output = StringIO.StringIO()
                im.save(output, 'JPEG')
                bucket.put_object(o_image, output.getvalue())
                output.close()
                href = "'" + bucket.generate_url(o_image) + "'"
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], o_image))
                (x, y) = im.size  # read image size
                x_s = 146  # define standard widt
                y_s = y * x_s / x  # calc height based on standard width
                # resize image with high-quality
                out = im.resize((x_s, y_s), Image.ANTIALIAS)
                s_image = save_name(filename, "_s_")
                output = StringIO.StringIO()
                out.save(output, 'JPEG')
                bucket.put_object(s_image, output.getvalue())
                output.close()
                src = "'" + bucket.generate_url(s_image) + "'"
                #out.save(os.path.join(app.config['UPLOAD_FOLDER'], s_image))
                #href = "'uploads/"+o_image+"'"
                #src = "'uploads/"+s_image+"'"
                c.execute(
                    'INSERT INTO `naaln_photo` (`id`, `blog_id`, `href`, `src`) VALUES (NULL, %s, %s, %s '');' %
                    (bid, href, src))
                g.db.commit()

    return render_template('New/new.html', info=info)


@app.route('/<int:y>/<int:m>/<int:d>/<k>')
def paper(y, m, d, k):
    c = g.db.cursor()
    time = str(y) + '-' + str(m) + '-' + str(d)
    c.execute(
        'SELECT id, title, subname, article, color, time, location, content, tags FROM `naaln_blog` WHERE `subname` LIKE %s AND `time` = \"%s\" ORDER BY `time` limit 1' % ("'"+k+"'", time))
    msgs = list(c.fetchall())
    blogs = []
    for id, title, subname, article, color, time, location, content, tags in msgs:
        ttags = tags
        tags = []
        for tag in ttags.split(" "):
            # tag = [tag]
            tags.append(tag)
        c.execute(
            'SELECT `photo_id` FROM `naaln_hero` WHERE `blog_id` = %s' % id)
        hero = list(c.fetchall())[0][0]
        c.execute(
            'select href, src, alt from naaln_photo where blog_id =%s and id !=%s' %
            (id, hero))
        photos = list(c.fetchall())
        c.execute(
            'select href, src, alt from naaln_photo where id = %s' % hero)
        pictures = list(c.fetchall())
        blog = [id, title, subname, article, color, hero,
                time, location, content, tuple(tags), photos, pictures]
        blogs.append(blog)
    # print blogs
    return render_template('Paper/index.html', msgs=tuple(blogs))


@app.route('/<int:y>-<int:m>-<int:d>/<k>')
def repaper(y, m, d, k):
    print y, m, d, k
    return redirect('/' + str(y) + '/' + str(m) + '/' + str(d) + '/' + k, 302)
