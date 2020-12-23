from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# TODO: USE JSON TO STORE URI & OTHER IMP STUFF

# import json
#
# with open('config.json', 'r') as c:pip
#     json = json.load(c)["json"]


app = Flask(__name__)
app.secret_key = "76^)(HEY,BULK-MAILER-HERE!)(skh390880213%^*&%6h&^&69lkjw*&kjh"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bulkmailer.db"
db = SQLAlchemy(app)

x = datetime.now()
time = x.strftime("%c")

class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    subscribers = db.relationship('Subscribers',cascade = "all,delete", backref='subscribers')

class Subscribers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    gid = db.Column(db.Integer, db.ForeignKey('groups.id'))

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
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

@app.route('/dashboard')
def dashboard_page():
    return render_template('index.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/register.html')
def register_page():
    return render_template('register.html')

@app.route('/forgot-password.html')
def forgot_page():
    return render_template('forgot-password.html')


@app.route('/view/groups')
def group_page():
    post = Groups.query.order_by(Groups.id).all()
    # print(time)
    return render_template('group_list.html', post=post)

@app.route('/new/group', methods=['POST'])
def submit_new_group():
    if(request.method=='POST'):
        group_name = request.form.get('groupname')
        entry = Groups(name=group_name, date=time)
        db.session.add(entry)
        db.session.commit()
        # flash("New group added successfully!", "success")
    return redirect('/view/groups')

@app.route("/delete/group/<string:id>", methods = ['GET'])
def delete_group(id):
    delete_group = Groups.query.filter_by(id=id).first()
    db.session.delete(delete_group)
    db.session.commit()
    # flash("Group deleted successfully!", "success")
    return redirect('/view/groups')

@app.route('/view/subscribers/<string:number>')
def subscribers_page(number):
    post = Subscribers.query.filter_by(gid=number).all()
    # print(post)
    return render_template('group_members.html', post=post)

@app.route('/delete/subscriber/<string:gid>/<string:number>', methods=['GET'])
def delete_subscriber(gid, number):
    delete_subscriber = Subscribers.query.filter_by(id=number).first()
    db.session.delete(delete_subscriber)
    db.session.commit()
    # flash("subscriber deleted successfully!", "success")
    return redirect('/view/subscribers/'+str(gid))

@app.route('/mail.html')
def mail_page():
    return render_template('mail.html')

@app.route('/group_members.html')
def group_members():
    return render_template('group_members.html')

@app.route('/user_list.html')
def userlist_page():
    return render_template('user_list.html')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
