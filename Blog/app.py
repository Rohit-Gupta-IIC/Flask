from flask import Flask, render_template, request, redirect, flash, session
from flask_ckeditor import CKEditor
from flask_mysqldb import MySQL
import yaml, os
from flask_bootstrap import Bootstrap
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
Bootstrap(app)
CKEditor(app)

db= yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.urandom(24)
mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    resultvalue = cur.execute('Select * from blog')
    if resultvalue>0:
        blog = cur.fetchall()
        return render_template('index.html', blogs=blog)
    cur.close()
    return render_template('index.html',blogs=None)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userDeatils = request.form
        print(userDeatils['password'], userDeatils['confirm_password'])
        if userDeatils['confirm_password'] != userDeatils['password']:
            print("1")
            flash('Password donot match!! Try Again','danger')
            return render_template('register.html')
        else:
            print('3456')
            cur = mysql.connection.cursor()
            print("2")
            cur.execute("Insert into user(first_name, last_name, username, email, password) values(%s, %s, %s, %s, %s)",(userDeatils['first_name'], userDeatils['last_name'], userDeatils['username'], userDeatils['email'], generate_password_hash(userDeatils['password'])))
            print("3")
            mysql.connection.commit()
            cur.close()
            flash("Registration Succesfull! Please login","success")
            return redirect('/login/')
    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userDetails = request.form
        username = userDetails['username']
        cur = mysql.connection.cursor()
        resultvalue = cur.execute('select * from user where username=%s',([username]))
        if resultvalue>0:
            user = cur.fetchall()
            if check_password_hash(user[0]['password'], userDetails['password']):
                session['login'] = True;
                session['firstname'] = user[0]['first_name']
                session['lastname'] = user[0]['last_name']
                flash('Welcome'+session['firstname']+'! You have been successfully logged in', 'success')
            else:
                cur.close()
                flash('PAssword does not match', 'danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('User not found', 'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')

@app.route('/write-blogs/', methods=['GET', 'POST'])
def write_blog():
    if request.method == 'POST':
        blogpost = request.form
        title = blogpost['title']
        body = blogpost['body']
        author = session['firstname'] + ' '+ session['lastname']
        cur = mysql.connection.cursor()
        cur.execute('insert into blog(title, author, body) values (%s, %s, %s)', ([title, author, body]))
        mysql.connection.commit()
        cur.close()
        flash('Successfully posted new blog', 'success')
        return redirect('/')
    return render_template('write_blogs.html')

@app.route('/blogs/<int:id>/')
def blogs(id):
    cur = mysql.connection.cursor()
    resultvalue = cur.execute("select * from blog where blog_id={}".format(id))
    if resultvalue>0:
        blog = cur.fetchone()
        return render_template('blogs.html', blog=blog)
    return 'Blog not found'

@app.route('/my-blogs/')
def my_blogs():
    author = session['firstname'] + ' '+ session['lastname']
    cur= mysql.connection.cursor()
    resultvalue = cur.execute('select * from blog where author =%s', [author])
    if resultvalue>0:
        my_blogs = cur.fetchall()
        return render_template('my_blogs.html',my_blogs=my_blogs)
    else:
        return render_template('my_blogs.html', my_blogs=None)

@app.route('/edit-blogs/<int:id>/', methods=['GET', 'POST'])
def edit_blog(id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cur.execute('update blog set title = %s, body=%s where blog_id=%s',(title, body, id))
        mysql.connection.commit()
        cur.close()
        flash('Blog updated successfully','success')
        return redirect('/blogs/{}'.format(id))
    cur =mysql.connection.cursor()
    resultvalue = cur.execute('select * from blog where blog_id = {}'.format(id))
    if resultvalue>0:
        blog = cur.fetchone()
        blog_form = {}
        blog_form['title'] = blog['title']
        blog_form['body'] = blog['body']
        return render_template('edit_blogs.html', blog_form=blog_form)

@app.route('/delete-blog/<int:id>/', methods=['GET','POST'])
def delete_blog(id):
    cur = mysql.connection.cursor()
    cur.execute('delete from blog where blog_id={}'.format(id))
    mysql.connection.commit()
    flash('Your blog has been deleted', 'success')
    return redirect('/my-blogs')

@app.route('/logout/')
def logout():
    session.clear()
    flash("You have been logged out", 'info')
    return redirect('/')

if __name__ == '__main__':
    app.run()
