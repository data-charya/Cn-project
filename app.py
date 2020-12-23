from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# TODO: USE JSON TO STORE URI & OTHER IMP STUFF

# import json
#
# with open('config.json', 'r') as c:pip
#     json = json.load(c)["json"]


app = Flask(__name__)
app.secret_key = "76^)(HEY,BULK-MAILER-HERE!)(skh390880213%^*&%6h&^&69lkjw*&kjh"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bulkmailer.db"
db = SQLAlchemy(app)

class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    subscribers = db.relationship('Subscribers', backref='subscribers')

class Subscribers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    gid = db.Column(db.Integer, db.ForeignKey('groups.id'))

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(50), nullable=False)

#TODO: IDEA IN IT

    # post = Subscribers.query.filter_by(gid=1).all()
    # print(post)
    # elist=[]
    # for post in post:
    #     elist = elist + [post.email]
    # print(elist)

@app.route('/')
def dashboard_page():
    return render_template('index.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/tables.html')
def table_page():
    return render_template('tables.html')

@app.route('/mail.html')
def mail_page():
    return render_template('mail.html')

@app.route('/templates.html')
def templates_page():
    return render_template('templates.html')

@app.route('/templates/group_members.html')
def group_members():
    return render_template('group_members.html')

if __name__ == '__main__':
    app.run(debug=True)
