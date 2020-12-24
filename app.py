from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from passlib.hash import sha256_crypt
import json, random, string


# TODO: USE JSON TO STORE URI & OTHER IMP STUFF

with open('import.json', 'r') as c:
    json = json.load(c)["jsondata"]


app = Flask(__name__)
app.secret_key = "76^)(HEY,BULK-MAILER-HERE!)(skh390880213%^*&%6h&^&69lkjw*&kjh"
app.config['SQLALCHEMY_DATABASE_URI'] = json["databaseUri"]
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return Organization.get(user_id)


class Group(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    subscribers = db.relationship('Subscriber',cascade = "all,delete", backref='subscribers')

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

class Organization(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(50), nullable=False)


letters = string.ascii_letters
new_password = ''.join(random.choice(letters) for i in range(8))

x = datetime.now()
time = x.strftime("%c")
#TODO: IDEA IN IT

    # post = Subscribers.query.filter_by(gid=1).all()
    # print(post)
    # elist=[]
    # for post in post:
    #     elist = elist + [post.email]
    # print(elist)

#TODO: MAIL CONFIG PART

    # subject = " Some String "
    # content = "<html> </html>"
    # message = Mail(
    #     from_email=('something@bulkmailer.cf', 'Some Name'),
    #     to_emails="to mail",
    #     subject=subject,
    #     html_content=content)
    # try:
    #     sg = SendGridAPIClient(json['sendgridapi'])
    #     response = sg.send(message)
    #     # flash("You will receive a mail shortly. Password rested successfully!", "success")
    #     # print(response.status_code)
    #     # print(response.body)
    #     # print(response.headers)
    # except Exception as e:
    #     print("Error!")

@app.route('/register',methods = ['GET', 'POST'])
def register_page():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if(password!=password2):
            # flash("Password unmatched!", "danger")
            return render_template('register.html', json=json)
        else:
            password = sha256_crypt.encrypt(password)
            response = Organization.query.filter_by(email=email).first()
            if(response==None):
                entry = Organization(name=name, email=email, password=password,lastlogin=datetime.now(), date=time, status=0)
                db.session.add(entry)
                db.session.commit()
                # flash("Now contact your organization head for account activation!", "success")
                subject = "Welcome aboard " + name + "!"
                content = '<strong>Hey</strong><br><br>Thanks for subscribing.<br>Now contact your organization head for account activation.<br>We are available 24*7 to help you.<br>Happy Learning<br><br>Regards,<br>CGV Support<br><br<br><br>Please do not reply to this email it is an automated email.'
                message = Mail(
                    from_email=('cgv.support@sdlsmartlabs.co.in', 'CGV SUPPORT TEAM'),
                    to_emails=email,
                    subject=subject,
                    html_content=content)
                try:
                    sg = SendGridAPIClient(json['sendgridapi'])
                    response = sg.send(message)
                    # flash('Email Sent Successfully!', success)
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                except Exception as e:
                    print("Error")
                    # flash("Error while sending mail!", "danger")
            else:
                # flash("User exist!", "danger")
                return render_template('register.html', json=json)

    return render_template('register.html', json=json)

@app.route('/forgot', methods = ['GET', 'POST'])
def forgot_password_page():
    if (request.method == 'POST'):
        email=request.form.get('email')
        post = Organization.query.filter_by(email=email).first()
        if(post!=None):
            if(post.email==json["admin_email"]):
                pass
                # flash("You can't reset password of administrator!", "danger")
            else:
                passwordemial = new_password
                post.password = sha256_crypt.encrypt(new_password)
                db.session.commit()
                subject = "New Password Generated "+passwordemial
                content = "Hello,<br>Greatings from Bulk Mailer Team!<br><br>We have reseted your password.<br><br>We are available 24*7 to help you.<br>Happy Learning<br><br>Regards,<br>Team Bulk Mailer<br><br<br><br>Please do not reply to this email it is an automated email."
                message = Mail(
                    from_email=('resetpassword@bulkmailer', 'Bulk Mailer Reset Password'),
                    to_emails=email,
                    subject=subject,
                    html_content=content)
                try:
                    sg = SendGridAPIClient(json['sendgridapi'])
                    response = sg.send(message)
                    # flash("You will receive a mail shortly. Password rested successfully!", "success")
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                except Exception as e:
                    print("Error!")
        elif(post==None):
                # flash("We didn't find your account!", "danger")
                return render_template('forgot-password.html', json=json)

    return render_template('forgot-password.html', json=json)


@app.route('/view/groups')
def group_page():
    post = Group.query.order_by(Group.id).all()
    # print(time)
    return render_template('group_list.html', post=post)

@app.route('/new/group', methods=['POST'])
def submit_new_group():
    if(request.method=='POST'):
        group_name = request.form.get('groupname')
        entry = Group(name=group_name, date=time)
        db.session.add(entry)
        db.session.commit()
        # flash("New group added successfully!", "success")
    return redirect('/view/groups')

@app.route("/delete/group/<int:id>", methods = ['GET'])
def delete_group(id):
    delete_group = Group.query.filter_by(id=id).first()
    db.session.delete(delete_group)
    db.session.commit()
    # flash("Group deleted successfully!", "success")
    return redirect('/view/groups')

@app.route('/view/subscribers/<int:number>')
def subscribers_page(number):
    post = Subscriber.query.filter_by(group_id=number).all()
    response = Group.query.order_by(Group.id).all()
    # print(response)
    # print(post)
    return render_template('group_members.html', post=post, response=response)

@app.route('/new/subscribers', methods=['POST'])
def submit_new_subscribers():
    if(request.method=='POST'):
        email = request.form.get('email')
        gid = request.form.get('gid')
        entry = Subscriber(email=email, date=time, group_id=gid)
        db.session.add(entry)
        db.session.commit()
        # flash("New subscriber added successfully!", "success")
    return redirect('/view/subscribers/' + str(gid))

@app.route('/delete/subscriber/<int:gid>/<int:number>', methods=['GET'])
def delete_subscriber(gid, number):
    delete_subscriber = Subscriber.query.filter_by(id=number).first()
    db.session.delete(delete_subscriber)
    db.session.commit()
    # flash("subscriber deleted successfully!", "success")
    return redirect('/view/subscribers/'+str(gid))

@app.route('/mail')
def mail_page():
    return render_template('mail.html')

@app.route('/groups')
def groups_page():
    return render_template('group_list.html')

@app.route('/template')
def template_page():
    return render_template('templates.html')

@app.route('/')
def dash_page():
    return render_template('index.html')
# @app.errorhandler(404)
# def page_not_found(e):
#     # note that we set the 404 status explicitly
#     return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
