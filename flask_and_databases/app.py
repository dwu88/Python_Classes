from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
from send_email import send_mail

'''
    sqlalchemy database url format:
    postgresql://username:password@localhost/database_name
'''
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=""
db=SQLAlchemy(app)

class Data(db.Model):
    __tablename__="data"
    id=db.Column(db.Integer,primary_key=True)
    email_=db.Column(db.String(120),unique=True)
    height_=db.Column(db.Integer)

    def __init__(self,email_,height_):
        self.email_=email_
        self.height_=height_

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success", methods=['POST'])
def success():
    if request.method == 'POST':
        email=request.form["email_name"]
        height = request.form["height_name"]
        send(email,height)
        if db.session.query(Data).filter(Data.email_ == email).count() == 0:
            data=Data(email,height)
            db.session.add(data)
            db.session.commit()
            return render_template("success.html")
    return render_template("index.html",
                        text="Duplicate email found! Try a new email address")

if __name__ == '__main__':
    app.debug = True
    app.run()