# Flask is imported to support the basic functions
from flask import Flask
# render_template is imported to enable us to laod html pages
from flask import render_template
# url_for is imported to create urls
from flask import url_for
# redirect is imported to redirect to the given webpage
from flask import redirect
# Bootstrap is imported to use Bootstrap
from flask_bootstrap import Bootstrap
# MySQL will provide us with basic SQL Functions
from flask_mysqldb import MySQL
# YAML is used to process yaml files
import yaml
# request is used to check for 'Get' and 'Post' requests
from flask import request

app = Flask(__name__)
Bootstrap(app)

db= yaml.full_load(open('db.yaml'))
print(db['mysql_host'])
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB']= db['mysql_db']

mysql = MySQL(app)

# following demonstrates handling errors i.e. client and server error
@app.errorhandler(404)
def page_not_found(e):
    return 'This page doesnot exist'

@app.route('/demomysql')
def demo4():
    cursor = mysql.connection.cursor()

    cursor.execute("INSERT into user values (%s)",['mike'])
    mysql.connection.commit()
    result_value = cursor.execute("Select * from user")
    mysql.connection.commit()
    if result_value>0:
        users = cursor.fetchall()
        print(str(users))
        return users[0][0]
    else:
        return render_template('index.html')

# in the following we added methods=['GET','POST'], to allow the post request to work as well, all route by default acceot get request
@app.route('/', methods=['GET','POST'])
def hello_world():
    if request.method == 'POST':
        return ('Successfull registered ' + request.form['password'])
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

## the following code demonstrates how we can create link using url_for
@app.route('/demo')
def demo_url_for():
    return url_for('about')

# the following code demonstrates how we can redirect to a given webpage
@app.route('/demo1')
def demo1():
    return redirect(url_for('about'))

# the following code demonstrates the use of jinja
@app.route('/demo2')
def demo2():
    fruits = ['Apple', 'Orange']
    return render_template('jinja_demo.html', fruits=fruits)

# example of jinja template
@app.route('/demo3')
def jinja_about():
    return render_template('jinja_about_demo.html')

# adding styles using Bootstrap
@app.route('/css')
def css():
    return render_template('css.html')

if __name__ == '__main__':
    app.run(debug=True)