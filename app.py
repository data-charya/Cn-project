from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from passlib.hash import sha256_crypt
import json, random, string, psycopg2


# TODO: USE JSON TO STORE URI & OTHER IMP STUFF
#load import.json file containing database uri, admin email and other impt info
with open('import.json', 'r') as c:
    json = json.load(c)["jsondata"]

#create a Flask app and setup its configuration
app = Flask(__name__)
app.secret_key = "76^)(HEY,BULK-MAILER-HERE!)(skh390880213%^*&%6h&^&69lkjw*&kjh"
app.config['SQLALCHEMY_DATABASE_URI'] = json["databaseUri"]
db = SQLAlchemy(app)

#use LoginManager to provide login functionality and do some initial confg
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

#function to load the currently active user
@login_manager.user_loader
def load_user(user_id):
    return Organization.query.get(user_id)

'''DATABASE MODELS'''
#represents a group of users to whom a specific email can be sent
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    subscribers = db.relationship('Subscriber',cascade = "all,delete", backref='subscribers')

#represents a subscriber that belongs to a group
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

#represents an email template
class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(50), nullable=False)

#represents a user in an organisation
#currently only one organisation with multiple users is supported
class Organization(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Integer , nullable=False)
    date = db.Column(db.String(50), nullable=False)
'''END OF DATABASE MODELS'''

#generate a random 8 lettered password for forgot password
letters = string.ascii_letters
new_password = ''.join(random.choice(letters) for i in range(8))

#convert the current datetime to string, to be stored in the db
x = datetime.now()
time = x.strftime("%c")

#domain name
domain='@bulkmailer.cf'
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

#login route
@app.route('/login', methods = ['GET', 'POST'])
def login():
    #check if user is authenticated
    if current_user.is_authenticated:
        #if true, go to the dash page
        return redirect(url_for('dash_page'))
    #check if a form has been submitted i.e., user has tried to login
    if (request.method == 'POST'):
        #get the data in the email, password, and remember me fields
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        #get user with the email entered by querying the database
        user = Organization.query.filter_by(email=email).first()
        #check if user exists
        if not user:
            #if user doesn't exist i.e., email not found, flash an error
            flash('Valid account not found!', 'danger')
            return render_template('login.html', json=json)
        elif ( sha256_crypt.verify(password, user.password ) == 1) and (user.status == 1):
            #if user exists and correct password has been entered and the user's account has been activated
            #update the last login to current date and add it to the db
            user.date = time
            db.session.add(user)
            db.session.commit()
            #log the user in using login_user
            login_user(user, remember=remember)
            #go to the page that the user tried to access if exists
            #otherwise go to the dash page
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dash_page'))
        else:
            #user doesn't exist so flash an error
            flash('Account not activated or invalid credentials!', 'danger')
    return render_template('login.html', json=json)

#logout route
@app.route('/logout')
@login_required
def logout():
    #log the user out using logout_user, flash a msg and go to the login page
    logout_user()
    flash('Logged Out Successfully!', 'success')
    return redirect(url_for('login'))

#register route
@app.route('/register',methods = ['GET', 'POST'])
def register_page():
    #check if form has been submitted i.e., user has tried to register
    if (request.method == 'POST'):
        #get the data in name, email, and password fields
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        #check if passwords match
        if(password!=password2):
            #if not, flash an error msg
            flash("Password unmatched!", "danger")
            return render_template('register.html', json=json)
        else:
            #generate the hashed password
            password = sha256_crypt.hash(password)
            response = Organization.query.filter_by(email=email).first()
            #check if the email already exists in the db
            if not response:
                #add the user to the db using the details entered and flash a msg
                entry = Organization(name=name, email=email, password=password, date=time, status=0)
                db.session.add(entry)
                db.session.commit()
                flash("Now contact your organization head for account activation!", "success")
                #generate the welcome email to be sent to the user
                subject = "Welcome aboard " + name + "!"
                content = '''<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><title>Reset Your Password</title> <!--[if !mso]> --><meta http-equiv="X-UA-Compatible" content="IE=edge"> <!--<![endif]--><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><style type="text/css">#outlook a{padding:0}.ReadMsgBody{width:100%}.ExternalClass{width:100%}.ExternalClass *{line-height:100%}body{margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}table,td{border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt}img{border:0;height:auto;line-height:100%;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic}p{display:block;margin:13px 0}</style><style type="text/css">@media only screen and (max-width:480px){@-ms-viewport{width:320px}@viewport{width:320px}}</style><style type="text/css">@media only screen and (min-width:480px){.mj-column-per-100{width:100%!important}}</style></head><body style="background: #f0f0f0;"><div class="mj-container" style="background-color:#f0f0f0;"><table role="presentation" cellpadding="0" cellspacing="0" style="background:#f0f0f0;font-size:0px;width:100%;" border="0"><tbody><tr><td><div style="margin:0px auto;max-width:600px;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;"><div style="font-size:1px;line-height:30px;white-space:nowrap;">&#xA0;</div></td></tr></tbody></table></div></td></tr></tbody></table></div></td></tr></tbody></table><div style="margin:0px auto;max-width:600px;background:#FFFFFF;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;background:#FFFFFF;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:9px 0px 9px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;padding:25px 25px 25px 25px;" align="center"><table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-spacing:0px;" align="center" border="0"><tbody><tr><td style="width:204px;"> <img alt="" title="" height="100px" width="100px" src="https://cdn.discordapp.com/attachments/577137963985534994/791571694803353610/favicon.ico" style="border:none;border-radius:0px;display:block;font-size:13px;outline:none;text-decoration:none;width:100%;height:auto;" width="204"></td></tr></tbody></table></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 15px 0px 15px;" align="center"><div style="cursor:auto;color:#333333;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><h3 style="font-family: Helvetica, sans-serif; font-size: 24px; color: #333333; line-height: 50%;">Hey, Welcome!</h3></div></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 50px 0px 50px;" align="center"><div style="cursor:auto;color:#333333;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p>Now contact your organization head for account activation.</p></div></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:20px 25px 20px 25px;padding-top:10px;padding-left:25px;" align="center"><table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:separate;" align="center" border="0"><tbody><tr><td style="border:none;border-radius:5px;color:#FFFFFF;cursor:auto;padding:10px 25px;" align="center" valign="middle" bgcolor="#4DAA50"><a href="https://bulkmailer.cf" style="text-decoration: none; background: #4DAA50; color: #FFFFFF; font-family: Helvetica, sans-serif; font-size: 19px; font-weight: normal; line-height: 120%; text-transform: none; margin: 0px;" target="_blank">Visit Website</a></td></tr></tbody></table></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 47px 0px 47px;" align="center"><div style="cursor:auto;color:#333333;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p><span style="font-size:14px;"><strong>Questions?&#xA0;</strong><br>Email us at <a href="mailto:email@bulkmailer.cf" style="color: #555555;">email@bulkmailer.cf</a>.&#xA0;</span></p></div></td></tr></tbody></table></div></td></tr></tbody></table></div><table role="presentation" cellpadding="0" cellspacing="0" style="background:#f0f0f0;font-size:0px;width:100%;" border="0"><tbody><tr><td><div style="margin:0px auto;max-width:600px;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 98px 0px 98px;" align="center"><div style="cursor:auto;color:#777777;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p><span style="font-size:12px;"><a href="https://bulkmailer.cf" style="color: #555555;">TERMS OF SERVICE</a> | <a href="https://bulkmailer.cf" style="color: #555555;">PRIVACY POLICY</a><br>&#xA9; 2020 Bulk Mailer<br><a href="https://bulkmailer.cf/unsubscribe" style="color: #555555;">UNSUBSCRIBE</a></span></p></div></td></tr></tbody></table></div></td></tr></tbody></table></div></td></tr></tbody></table></div></body></html>'''
                message = Mail(
                    from_email=('register@bulkmailer.cf', 'Bulk Mailer Register'),
                    to_emails=email,
                    subject=subject,
                    html_content=content)
                try:
                    #using the sendgrid api, send the email to the user's email
                    sg = SendGridAPIClient(json['sendgridapi'])
                    response = sg.send(message)
                    # flash('Email Sent Successfully!', success)
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                except Exception as e:
                    #if an error occurs flash a msg
                    print("Error")
                    flash("Error while sending mail!", "danger")
                return redirect(url_for('login'))
            else:
                #user exists so flash an error
                flash("User exists!", "danger")
                return render_template('register.html', json=json)
    return render_template('register.html', json=json)

#forgot password route
@app.route('/forgot', methods = ['GET', 'POST'])
@login_required
def forgot_password_page():
    #check if form has been submitted
    if (request.method == 'POST'):
        #get the email entered
        email=request.form.get('email')
        #get the user from the db
        post = Organization.query.filter_by(email=email).first()
        if post:
            #if user exists
            if(post.email==json["admin_email"]):
                #if user tried to reset admin password
                flash("You can't reset password of administrator!", "danger")
                return render_template('forgot-password.html', json=json)
            else:
                #hash the new password generated
                passwordemail = new_password
                post.password = sha256_crypt.hash(new_password)
                db.session.commit()
                #generate the forgot password email to be sent to the user
                subject = "Password Generated : " + passwordemail
                content = '''<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><title>Reset Your Password</title> <!--[if !mso]> --><meta http-equiv="X-UA-Compatible" content="IE=edge"> <!--<![endif]--><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><style type="text/css">#outlook a{padding:0}.ReadMsgBody{width:100%}.ExternalClass{width:100%}.ExternalClass *{line-height:100%}body{margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}table,td{border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt}img{border:0;height:auto;line-height:100%;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic}p{display:block;margin:13px 0}</style><style type="text/css">@media only screen and (max-width:480px){@-ms-viewport{width:320px}@viewport{width:320px}}</style><style type="text/css">@media only screen and (min-width:480px){.mj-column-per-100{width:100%!important}}</style></head><body style="background: #f0f0f0;"><div class="mj-container" style="background-color:#f0f0f0;"><table role="presentation" cellpadding="0" cellspacing="0" style="background:#f0f0f0;font-size:0px;width:100%;" border="0"><tbody><tr><td><div style="margin:0px auto;max-width:600px;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;"><div style="font-size:1px;line-height:30px;white-space:nowrap;">&#xA0;</div></td></tr></tbody></table></div></td></tr></tbody></table></div></td></tr></tbody></table><div style="margin:0px auto;max-width:600px;background:#FFFFFF;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;background:#FFFFFF;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:9px 0px 9px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;padding:25px 25px 25px 25px;" align="center"><table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-spacing:0px;" align="center" border="0"><tbody><tr><td style="width:204px;"> <img alt="" title="" height="100px" width="100px" src="https://cdn.discordapp.com/attachments/577137963985534994/791571694803353610/favicon.ico" style="border:none;border-radius:0px;display:block;font-size:13px;outline:none;text-decoration:none;width:100%;height:auto;" width="204"></td></tr></tbody></table></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 15px 0px 15px;" align="center"><div style="cursor:auto;color:#333333;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><h3 style="font-family: Helvetica, sans-serif; font-size: 24px; color: #333333; line-height: 50%;">Your password has been reset successfully</h3></div></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 50px 0px 50px;" align="center"><div style="cursor:auto;color:#333333;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p>Forgot your password or need to change it? No problem.</p></div></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:20px 25px 20px 25px;padding-top:10px;padding-left:25px;" align="center"><table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:separate;" align="center" border="0"><tbody><tr><td style="border:none;border-radius:5px;color:#FFFFFF;cursor:auto;padding:10px 25px;" align="center" valign="middle" bgcolor="#4DAA50"><a href="#" style="text-decoration: none; background: #4DAA50; color: #FFFFFF; font-family: Helvetica, sans-serif; font-size: 19px; font-weight: normal; line-height: 120%; text-transform: none; margin: 0px;" target="_blank">Login</a></td></tr></tbody></table></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 47px 0px 47px;" align="center"><div style="cursor:auto;color:#333333;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p><span style="font-size:14px;"><strong>Questions?&#xA0;</strong><br>Email us at <a href="mailto:email@bulkmailer.cf" style="color: #555555;">email@bulkmailer.cf</a>.&#xA0;</span></p></div></td></tr></tbody></table></div></td></tr></tbody></table></div><table role="presentation" cellpadding="0" cellspacing="0" style="background:#f0f0f0;font-size:0px;width:100%;" border="0"><tbody><tr><td><div style="margin:0px auto;max-width:600px;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 98px 0px 98px;" align="center"><div style="cursor:auto;color:#777777;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p><span style="font-size:12px;"><a href="https://bulkmailer.cf" style="color: #555555;">TERMS OF SERVICE</a> | <a href="https://bulkmailer.cf" style="color: #555555;">PRIVACY POLICY</a><br>&#xA9; 2020 Bulk Mailer<br><a href="https://bulkmailer.cf/unsubscribe" style="color: #555555;">UNSUBSCRIBE</a></span></p></div></td></tr></tbody></table></div></td></tr></tbody></table></div></td></tr></tbody></table></div></body></html>'''
                message = Mail(
                    from_email=('resetpassword@bulkmailer.cf', 'Bulk Mailer Reset Password'),
                    to_emails=email,
                    subject=subject,
                    html_content=content)
                try:
                    #using the sendgrid api, send the email to the user's email
                    sg = SendGridAPIClient(json['sendgridapi'])
                    response = sg.send(message)
                    flash("You will receive a mail shortly. Password rested successfully!", "success")
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                except Exception as e:
                    #if error occurs flash a msg
                    print("Error!")
        else:
            #user doesn't exist
            flash("We didn't find your account!", "danger")
            return render_template('forgot-password.html', json=json)

    return render_template('forgot-password.html', json=json)

#route to view groups
@app.route('/view/groups')
@login_required
def group_page():
    #get all the groups in the db ordered by id
    groups = Group.query.order_by(Group.id).all()
    return render_template('group_list.html', groups=groups)

#route to add a new group
@app.route('/new/group', methods=['POST'])
@login_required
def submit_new_group():
    #check if form has been submitted
    if(request.method=='POST'):
        #get the group name
        group_name = request.form.get('groupname')
        entry = Group(name=group_name, date=time)
        db.session.add(entry)
        db.session.commit()
        flash("New group added successfully!", "success")
    return redirect('/view/groups')

@app.route("/delete/group/<int:id>", methods = ['GET'])
@login_required
def delete_group(id):
    delete_group = Group.query.filter_by(id=id).first()
    if(delete_group.id==3):
        flash("You can not delete default group!", 'warning')
        return redirect('/view/groups')
    else:
        db.session.delete(delete_group)
        db.session.commit()
        flash("Group deleted successfully!", "danger")
        return redirect('/view/groups')

@app.route("/activate/user/<int:id>", methods = ['GET'])
@login_required
def activate_user(id):
    activate_user = Organization.query.filter_by(id=id).first()
    if(activate_user.status==1):
        activate_user.status=0
        flash("User deactivated successfully!", "warning")
    else:
        activate_user.status=1
        flash("User activated successfully!", "success")
    db.session.commit()
    return redirect('/view/users')

@app.route("/delete/user/<int:id>", methods = ['GET'])
@login_required
def delete_user(id):
    delete_user = Organization.query.filter_by(id=id).first()
    if(delete_user.email==json["admin_email"]):
        flash("You cannot delete administrator", "warning")
        return redirect('/view/users')
    else:
        db.session.delete(delete_user)
        db.session.commit()
        flash("User deleted successfully!", "danger")
        return redirect('/view/users')

@app.route("/delete/template/<int:id>", methods = ['GET'])
@login_required
def delete_template(id):
    delete_template = Template.query.filter_by(id=id).first()
    db.session.delete(delete_template)
    db.session.commit()
    flash("Template deleted successfully!", "danger")
    return redirect('/view/templates')

@app.route('/view/subscribers/<int:number>')
@login_required
def subscribers_page(number):
    post = Subscriber.query.filter_by(group_id=number).all()
    response = Group.query.order_by(Group.id).all()
    # print(response)
    # print(post)
    return render_template('group_members.html', post=post, response=response)

@app.route('/new/subscribers', methods=['POST'])
@login_required
def submit_new_subscribers():
    if(request.method=='POST'):
        email = request.form.get('email')
        gid = request.form.get('gid')
        entry = Subscriber(email=email, date=time, group_id=gid)
        db.session.add(entry)
        db.session.commit()
        flash("New subscriber added successfully!", "success")
    return redirect('/view/subscribers/' + str(gid))

@app.route('/delete/subscriber/<int:gid>/<int:number>', methods=['GET'])
@login_required
def delete_subscriber(gid, number):
    delete_subscriber = Subscriber.query.filter_by(id=number).first()
    db.session.delete(delete_subscriber)
    db.session.commit()
    flash("Subscriber deleted successfully!", "danger")
    return redirect('/view/subscribers/'+str(gid))

    # post = Subscribers.query.filter_by(gid=1).all()
    # print(post)
    # elist=[]
    # for post in post:
    #     elist = elist + [post.email]
    # print(elist)


@app.route('/mail', methods=['POST', 'GET'])
@login_required
def mail_page():
    if(request.method=='POST'):
        username = request.form.get('username')
        name = request.form.get('name')
        subject = request.form.get('subject')
        group = request.form.get('group')
        html_content = request.form.get('editordata')
        html_content = html_content + '''<table role="presentation" cellpadding="0" cellspacing="0" style="background:#f0f0f0;font-size:0px;width:100%;" border="0"><tbody><tr><td><div style="margin:0px auto;max-width:600px;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 98px 0px 98px;" align="center"><div style="cursor:auto;color:#777777;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p><span style="font-size:12px;"><a href="https://bulkmailer.cf" style="color: #555555;">TERMS OF SERVICE</a> | <a href="https://bulkmailer.cf" style="color: #555555;">PRIVACY POLICY</a><br>© 2020 Bulk Mailer<br><a href="https://bulkmailer.cf/unsubscribe" style="color: #555555;">UNSUBSCRIBE</a></span></p></div></td></tr></tbody></table></div></td></tr></tbody></table></div></td></tr></tbody></table>'''
        fromemail = username+domain
        mailobj = Subscriber.query.filter_by(group_id=group).all()
        maillist = []
        for mailobj in mailobj:
            maillist = maillist + [mailobj.email]
        # print(maillist)
        message = Mail(
            from_email=(fromemail, name),
            to_emails=maillist,
            subject=subject,
            html_content=html_content)
        try:
            sg = SendGridAPIClient(json['sendgridapi'])
            response = sg.send(message)
            flash("Mail has been sent successfully!", "success")
            # print(response.status_code)
            # print(response.body)
            # print(response.headers)
        except Exception as e:
            # print("Error!")
            flash("Error due to invalid details entered!", "danger")
    group = Group.query.order_by(Group.id).all()
    mailtemp = Template.query.order_by(Template.id).all()
    return render_template('mail.html', group=group, template=mailtemp)


@app.route("/use/template/<int:id>", methods = ['GET'])
@login_required
def use_template(id):
    post = Template.query.filter_by(id=id).first()
    group = Group.query.order_by(Group.id).all()
    mailtemp = Template.query.order_by(Template.id).all()
    return render_template('mail2.html', group=group, template=mailtemp, post=post)

@app.route("/use/group/<int:id>", methods = ['GET'])
@login_required
def use_group(id):
    post = Group.query.filter_by(id=id).first()
    mailtemp = Template.query.order_by(Template.id).all()
    return render_template('mail3.html', template=mailtemp, post=post)

@app.route('/view/templates')
@login_required
def template_page():
    template = Template.query.order_by(Template.id).all()
    return render_template('templates.html', template=template)

@app.route('/add/template', methods=['POST'])
@login_required
def add_template():
    if (request.method == 'POST'):
        link = request.form.get('link')
        name = request.form.get('name')
        editordata = request.form.get('editordata')
        entry = Template(name=name, date=time, content=editordata, link=link)
        db.session.add(entry)
        db.session.commit()
        flash('Template added successfully!', 'success')
        return redirect('/view/templates')


@app.route('/subscribe', methods=['GET', 'POST'])
def sub_page():
    if (request.method == 'POST'):
        email = request.form.get('email')
        check = Subscriber.query.filter_by(email=email).first()
        if(check==None):
            entry = Subscriber(email=email, date=time, group_id=3)
            db.session.add(entry)
            db.session.commit()
            # flash('Newsletter subscribed successfully!', 'success')
            return render_template('thankyou.html')
        else:
            flash('You have already subscribed!', 'danger')
            return render_template('error.html')


@app.route('/unsubscribe', methods=['GET', 'POST'])
def unsub_page():
    if (request.method == 'POST'):
        email = request.form.get('email')
        delete_subscriber = Subscriber.query.filter_by(email=email).first()
        if(delete_subscriber==None):
            flash('We did not find your data in our database!', 'danger')
            return render_template('error.html')
        else:
            db.session.delete(delete_subscriber)
            db.session.commit()
            flash('Newsletter unsubscribed  successfully!', 'success')
            return render_template('error.html')


@app.route('/')
@login_required
def dash_page():
    glen = len(Group.query.order_by(Group.id).all())
    slen = len(Subscriber.query.order_by(Subscriber.id).all())
    tlen = len(Template.query.order_by(Template.id).all())
    return render_template('index.html', glen=glen, slen=slen, tlen=tlen)

@app.route('/view/users')
@login_required
def users_page():
    users = Organization.query.order_by(Organization.id).all()
    return render_template('user_list.html', users=users)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
