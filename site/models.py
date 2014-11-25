# coding=utf-8
# from __future__ import with_statement


import os
import sys
import MySQLdb
from PIL import Image
import StringIO
import random
from datetime import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# configuration

import sae.const
from setting import *
import re
from werkzeug import secure_filename
import sae.storage
access_key = sae.const.ACCESS_KEY
secret_key = sae.const.SECRET_KEY
appname = sae.const.APP_NAME


def connect_db():
    return MySQLdb.connect(
        sae.const.MYSQL_HOST, sae.const.MYSQL_USER, sae.const.MYSQL_PASS,
        sae.const.MYSQL_DB, port=int(sae.const.MYSQL_PORT), charset='utf8')


def save_name(filename, size):
    ext = filename.rsplit('.', 1)[1]
    d = filename.rsplit('.', 1)[0]
    fn = datetime.now().strftime('%Y%m%d%H%M%S')
    fn = fn + '_%d' % random.randint(0, 100)
    name = os.path.join(d + size + fn + "." + ext)
    return name


class Posts:

    @staticmethod
    def add_a_post(title, time, location, tags, content, userid, rannew):
        conn = connect_db()
        c = conn.cursor()
        pic_count = Photos.get_count_by_rannew(userid, rannew)
        pic_hero = Photos.get_count_by_rannew(userid, rannew)
        if pic_count == 1 or (pic_count > 6 and len(content) < 250) or (pic_hero > 1):
            article = 'hpb'
        else:
            article = 'fpb'
        color = random.choice(
            ('blue', 'brown', 'green', 'orange', 'pink', 'purple', 'yellow'))
        naaln_posts = (title, article, color, time, location, content, tags)
        c.execute(
            "INSERT INTO `naaln_posts` (`title`, `article`, `color`, `time`, `location`, `content`, `tags`) \
            VALUES ('%s','%s','%s','%s','%s','%s','%s');" % naaln_posts)
        conn.commit()
        id = int(c.lastrowid)
        Photos.update_a_photo(id, userid, rannew)
        c.close()
        return id

    @staticmethod
    def get_news_count():
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT count(`id`) FROM `naaln_posts`')
        count = list(c.fetchall())[0][0]
        c.close()
        count = count if count else 1
        return count

    @staticmethod
    def get_per_count(page):
        page = page - 1
        count = Posts.get_news_count()
        pagecount = (count - 1) / POSTS_PER_PAGE + 1

    @staticmethod
    def get_news_by_page(page):
        page = page - 1
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT `id`, `title`, `article`, `color`, `time`, `location`, `content`, `tags` \
            FROM `naaln_posts` ORDER BY `time` DESC LIMIT %s,%s' % (page * POSTS_PER_PAGE, POSTS_PER_PAGE))
        msgs = list(c.fetchall())
        blogs = []
        for id, title, article, color, time, location, content, tags in msgs:
            photos = Photos.get_photos_by_pid(id)
            length = len(photos)
            blog = [id, title, article, color,
                    time, location, content, photos[1:length], [photos[0]]]
            blogs.append(blog)
        mess = tuple(blogs)
        c.close()
        return mess

    @staticmethod
    def get_all_posts():
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT `id`, `title`, `article`, `color`, `time`, `location`, `content` FROM `naaln_posts`')
        msgs = list(c.fetchall())
        c.close()

        return msgs


class Photos:

    @staticmethod
    def add_a_photo(href, src, alt, hero, userid, rannew):
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'INSERT INTO `naaln_photo`(`href`, `src`, `alt`, `hero`, `userid`, `rannew`) VALUES ("%s","%s","%s","%s","%s","%s")' % (href, src, alt, hero, userid, rannew))
        photos = list(c.fetchall())
        conn.commit()
        c.close()
        return photos

    @staticmethod
    def update_a_photo(pid, userid, rannew):
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'UPDATE `naaln_photo` SET `blog_id` = "%s" WHERE `userid` =%s and `rannew` ="%s"' % (pid, userid, rannew))
        photos = list(c.fetchall())
        conn.commit()
        c.close()
        return photos

    @staticmethod
    def get_photos_by_pid(id):
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT `href`, `src`, `alt` FROM `naaln_photo` WHERE `blog_id` =%s ORDER BY `hero` DESC' % id)
        photos = list(c.fetchall())
        c.close()
        return photos

    @staticmethod
    def get_count_by_rannew(userid, rannew):
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT count(`id`) FROM `naaln_photo` WHERE `userid` =%s and `rannew` ="%s"' % (userid, rannew))
        count = list(c.fetchall())
        c.close()
        return count[0][0]

    @staticmethod
    def get_hero_by_rannew(userid, rannew):
        conn = connect_db()
        c = conn.cursor()
        c.execute(
            'SELECT `hero` FROM `naaln_photo` WHERE `userid` =%s and `rannew` ="%s" and `hero`>0' % (userid, rannew))
        hero = list(c.fetchall())
        c.close()
        return hero[0][0]


class Users:

    @staticmethod
    def login(name, password):
        conn = connect_db()
        c = conn.cursor()

        c.execute(
            'SELECT `id`, `user`, `password` FROM `naaln_users` WHERE `user` ="%s"' % name)
        userinfo = c.fetchall()
        c.close()

        msg = {}
        if userinfo:
            for id, user, psd in userinfo:

                if password == psd:
                    msg['id'] = id
                    msg['state'] = 'successed'
                    msg['message'] = 'You logged in'
                else:
                    msg['state'] = 'fail'
                    msg['message'] = 'Invalid password'

        else:
            msg['state'] = 'fail'
            msg['message'] = 'Invalid username'
        return msg


class Upload:

    @staticmethod
    def img_x_y(img):
        im = Image.open(img)
        (x, y) = im.size
        return y / x + 1

    @staticmethod
    def upload_image(img, name='_o_', x_s=0, y_s=0):
        x_s = float(x_s)
        y_s = float(y_s)
        img.seek(0)
        bucket = sae.storage.Bucket('picture')
        bucket.put()
        filename = secure_filename(img.filename)

        im = Image.open(img)
        (x, y) = im.size
        x = float(x)
        y = float(y)
        out = im
        # 16/11
        rare = float(37) / float(25)
        if x_s > 0 and y_s == 0:
            if y > x:
                if y / x > rare:
                    print '1'
                    y_s = y / x * x_s
                    out = im.resize((int(x_s), int(y_s)), Image.ANTIALIAS)
                    y_c = (y_s - x_s * rare) / 2
                    box = (0, int(y_c), int(x_s), int(y_s - y_c))
                    out = out.crop(box)
                else:
                    print '2'
                    y_s = rare * x_s
                    x_s = x / y * y_s
                    out = im.resize((int(x_s), int(y_s)), Image.ANTIALIAS)
                    x_c = (x_s - y_s / rare) / 2
                    box = (int(x_c), 0, int(x_s - x_c), int(y_s))
                    out = out.crop(box)
            else:
                if x / y > rare:
                    print '3'
                    y_s = x_s / rare
                    x_s = x / y * y_s
                    out = im.resize((int(x_s), int(y_s)), Image.ANTIALIAS)
                    print x_s, y_s
                    x_c = (x_s - y_s * rare) / 2
                    print int(x_c), 0, int(y_s - x_c), int(y_s)
                    box = (int(x_c), 0, int(x_s - x_c), int(y_s))
                    out = out.crop(box)
                else:
                    print '4'
                    y_s = y / x * x_s
                    out = im.resize((int(x_s), int(y_s)), Image.ANTIALIAS)
                    y_c = (y_s - x_s / rare) / 2
                    box = (0, int(y_c), int(x_s), int(y_s - y_c))
                    out = out.crop(box)
        elif x_s == 0 and y_s > 0:
            x_s = x / y * y_s
            out = im.resize((int(x_s), int(y_s)), Image.ANTIALIAS)

        s_image = save_name(img.filename, name)
        output = StringIO.StringIO()
        out.save(output, 'PNG')

        bucket.put_object(s_image, output.getvalue())
        output.close()
        url = bucket.generate_url(s_image)

        return url
