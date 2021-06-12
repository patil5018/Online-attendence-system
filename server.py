from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import cross_origin
import base64
from io import BytesIO
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
import json
import face_recognition
import os
import json
# from flask_script import Manager
# from flask_migrate import Migrate, MigrateCommand

#conn = "mysql://root:root@localhost/attendence_app"
conn = "mysql://freedbtech_rootp:rootp@freedb.tech/freedbtech_attendenceapp"
#conn = "mysql://sql6412404:hDBj5k2wWL@sql6.freemysqlhosting.net/sql6412404"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = conn
db = SQLAlchemy(app)
picFolder=os.path.join('static','assets')
app.config['UPLOAD_FOLDER']=picFolder

# defining models for sql


class student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    branch = db.Column(db.String(255))
    year = db.Column(db.Integer)
    password = db.Column(db.String(255))


class teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    branch = db.Column(db.String(255))
    year = db.Column(db.Integer)


class meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meeting_link = db.Column(db.String(255))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    time_created = db.Column(db.DateTime(
        timezone=True), default=datetime.now())


class attendence(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stud_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'))
    attendance_time = db.Column(db.Integer)


#db.create_all()

# Initializing image recognition model
files_list = os.listdir("./trainingdata")

encoded_images = []

# image = face_recognition.load_image_file('./trainingdata/48.jpg')
# encoded_image = face_recognition.face_encodings(image)
# print(len(encoded_image))
# encoded_image2 = face_recognition.face_encodings(image)[0]
# encoded_images.append(encoded_image2)

print('Initializing image training model')

if any(files_list):
    for file in files_list:
        print(file)
        image = face_recognition.load_image_file("./trainingdata/"+str(file))
        encoded_image = face_recognition.face_encodings(image)[0]
        encoded_images.append(encoded_image)

print('Initialized')

#@cross_origin()
@app.route('/')
def hello_world():
    pic1=os.path.join(app.config['UPLOAD_FOLDER'],'S1.jpg')
    pic2=os.path.join(app.config['UPLOAD_FOLDER'],'S2.jpg')
    pic3=os.path.join(app.config['UPLOAD_FOLDER'],'S3.jpg')
    return render_template("home.html", s1=pic1, s2=pic2, s3=pic3)


# ______________TEACHER ROUTES

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        newuser = teacher.query.filter_by(email=request.form['email']).first()
        if newuser.password == request.form['password']:
            session['tid'] = newuser.id
            return redirect(url_for('teacher_def_meeting'))
        else:
            return render_template("teacher_login.html")
    else:
        return render_template("teacher_login.html")


@app.route('/teacher/logout')
def teacher_logout():
    session.pop('tid', None)
    return redirect(url_for('teacher_login'))


@app.route('/teacher/register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        print(request.form['email'])
        newteacher = teacher(name=request.form['name'],
                             email=request.form['email'],
                             password=request.form['password'],
                             branch=request.form['branch'],
                             year=request.form['year'])
        db.session.add(newteacher)
        db.session.commit()
        return render_template("teacher_register.html")
    else:
        return render_template("teacher_register.html")


@app.route('/teacher/create_meeting', methods=['GET', 'POST'])
def teacher_def_meeting():
    if 'tid' in session:
        # print(session['tid'])
        if request.method == 'POST':
            newmeeting = meeting(
                meeting_link=request.form['meeting_link'],
                teacher_id=session['tid']
            )
            db.session.add(newmeeting)
            db.session.commit()
            meet_now = meeting.query.filter_by(teacher_id=session['tid']).order_by(
                meeting.id.desc()).limit(1).all()
            return render_template("teacher_create_meeting.html", meet_id=meet_now[0].id)
        else:
            m_id = 'None'
            return render_template("teacher_create_meeting.html", meet_id=m_id)
    else:
        return redirect(url_for('teacher_login'))


@app.route("/teacher/attendence_report", methods=['GET', 'POST'])
def attendence_report():
    if 'tid' in session:
        if request.method == 'POST':
            # attendencedata = attendence.query.filter_by(
            #     meeting_id=request.form['meetingid'])
            # attendencedata = student.query().join(
            #     attendence, student.id == attendence.stud_id)\
            #     .filter(attendence.meeting_id == request.form['meetingid'])

            # for student, attendence in attendencedata:
            #     print(student.name, attendence.meet_id,
            #           attendence.attendance_time)

            queryOne = 'SELECT student.id, student.name, attendence.meeting_id, attendence.attendance_time from student INNER JOIN attendence ON student.id=attendence.stud_id WHERE attendence.meeting_id=' + \
                request.form['meetingid']
            result = db.engine.execute(queryOne)

            arr = []

            for i in result:
                record = {
                    "id": ""+str(i[0]),
                    "name": ""+str(i[1]),
                    "meeting_id": ""+str(i[2]),
                    "attendence_time": ""+str(i[3]*5)
                }
                arr.append(record)
                print(i[0])
                print(i[1])
                print(i[2])
                print(i[3])

            return render_template("attendence_report.html", attendenddata=arr)
        else:
            meetingdata = meeting.query.filter_by(
                teacher_id=session['tid']).all()
            return render_template("attendence_report.html", meetdata=meetingdata)
    else:
        return redirect(url_for('teacher_login'))


# ______________STUDENT ROUTES


@app.route('/api/student/register', methods=["POST"])
@cross_origin()
def get():
    req_data = request.get_json()

    # print(req_data['image'])
    # print(req_data['name'])

    print(req_data['name'])
    print(req_data['email'])
    print(req_data['branch'])
    print(req_data['year'])
    print(req_data['password'])

    newstudent = student(
        name=req_data['name'],
        email=req_data['email'],
        branch=req_data['branch'],
        year=int(req_data['year']),
        password=req_data['password']
    )
    db.session.add(newstudent)
    db.session.commit()

    print(newstudent.id)

    file = req_data['image']
    # print(req_data['image'])
    im = Image.open(BytesIO(base64.b64decode(file))).convert('RGB')
    newsize = (640, 480)
    im = im.resize(newsize)
    im.save('./trainingdata/'+str(newstudent.id)+'.jpg', 'JPEG')

    image = face_recognition.load_image_file(
        './trainingdata/'+str(newstudent.id)+'.jpg')
    encoded_image = face_recognition.face_encodings(image)
    print(len(encoded_image))
    encoded_image2 = face_recognition.face_encodings(image)[0]
    encoded_images.append(encoded_image2)

    return jsonify(message="you are registered succesfully")


@app.route('/student/register')
def student_register():
    return render_template('student_register.html')


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        newuser = student.query.filter_by(email=request.form['email']).first()
        if hasattr(newuser, 'password') and newuser.password == request.form['password']:
            session['sid'] = newuser.id
            return redirect(url_for('student_meeting_join'))
        else:
            return render_template("student_login.html")
    else:
        return render_template("student_login.html")


@app.route('/student/join_meeting')
def student_meeting_join():
    if 'sid' in session:
        return render_template("student_join_meeting.html")
    else:
        return redirect(url_for('student_login'))


@app.route('/student/logout')
def student_logout():
    session.pop('sid', None)
    return redirect(url_for('student_login'))

@app.route('/Aboutus')
def about1():
    return render_template("Aboutus.html")


@app.route('/api/student/register_to_meeting', methods=["POST"])
@cross_origin()
def register_to_meeting():
    try:
        req_data = request.get_json()

        file = req_data['image']
        # print(req_data['image'])
        im = Image.open(BytesIO(base64.b64decode(file))).convert('RGB')
        newsize = (640, 480)
        im = im.resize(newsize)
        im.save('./testdata/test.jpg', 'JPEG')

        image = face_recognition.load_image_file(
            './testdata/test.jpg')
        encoded_image = face_recognition.face_encodings(image)
        if len(encoded_image) > 0:
            encoded_image2 = face_recognition.face_encodings(image)[0]
            result = face_recognition.compare_faces(
                encoded_images, encoded_image2)
            if any(result):
                print("student_id "+str(session['sid']) +
                      " has joined the meeting_id "+str(req_data['meetingid']))
                user_attendence = attendence.query.filter_by(
                    stud_id=session['sid'],
                    meeting_id=int(req_data['meetingid'])
                ).first()
                if not user_attendence:
                    newattendence = attendence(
                        stud_id=session['sid'],
                        meeting_id=req_data['meetingid'],
                        attendance_time=0
                    )
                    db.session.add(newattendence)
                    db.session.commit()
                return jsonify(message="registered for meeting")
            else:
                return jsonify(message="face not recognized")
        else:
            return jsonify(message="no person present in camera")
    except:
        return jsonify(message="no person present in camera")


@app.route('/api/student/attend', methods=["POST"])
@cross_origin()
def verify_attendence():
    try:
        req_data = request.get_json()
        user_attendence = attendence.query.filter_by(
            stud_id=session['sid'],
            meeting_id=int(req_data['meetingid'])
        ).first()

        if user_attendence.attendance_time < 20:
            user_attendence.attendance_time = user_attendence.attendance_time + 1
            db.session.commit()

        return jsonify(message="verified")

    except requests.exceptions.RequestException as e:
        print(e)
        return jsonify(message="verified")


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
