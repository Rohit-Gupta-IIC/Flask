from flask import Flask, render_template, request, session, flash
from flask_mysqldb import MySQL
import yaml, os
# the following will be used to generate hash for the data
from werkzeug.security import generate_password_hash
# the following will be used to check if the encrypted and given data is same
from werkzeug.security import check_password_hash
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
# the following is used so that we can access the content as dictionary
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# the following is the security key to secure the session
app.config['SECRET_KEY'] = os.urandom(24)
mysql = MySQL(app)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        try:
            form = request.form
            nam = form['name']
            age = form['age']
            cursor = mysql.connection.cursor()
            ''' 
            # the following will encrypt the data as sha256
            nam = generate_password_hash(nam)
            # the following will decrypt the data from sha256
            nam = check_password_hash(nam)
             '''
            cursor.execute('Insert into employee(name, age) values (%s, %s)', (nam, age))
            mysql.connection.commit()
            flash('Successfully inserted data', 'success')
        except:
            flash("Failed to insert data", 'danger')
    return render_template('index.html')

@app.route('/em')
def employee():
    cursor = mysql.connection.cursor()
    result_value = cursor.execute('Select * from employee')
    if result_value>0:
        result = cursor.fetchall()
        # we use session to save data into a session varioble which can be accessed anytime anywhere
        session['username'] = result[0]['name']
        return render_template('employee.html', result=result)

if __name__ == '__main__':
    app.run()
