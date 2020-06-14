import pymongo
from flask import Flask, jsonify, request, render_template, url_for, redirect, send_file
from flask_pymongo import PyMongo
import json
from schemas import validate_user, validate_login, validate_search_institutions, validate_apply_for_room, \
    validate_confirmation, validate_contact_request, validate_profile
import datetime
from datetime import datetime as Dtime
from datetime import time as my_time
from bson.objectid import ObjectId
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity)
from flask_bcrypt import Bcrypt
from pyexcel_xls import get_data
import pandas as pd
import xlrd
from flask_mail import Mail, Message
import os
import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = 'classit.info@gmail.com'
EMAIL_PASSWORD = 'c1assit.support'


# msg = EmailMessage()
# msg['Subject'] = 'Hello'
# msg['From'] = EMAIL_ADDRESS
# msg['To'] = EMAIL_ADDRESS_RECIEVER
# msg.set_content('How are you?')
#
# with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#     smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#     smtp.send_message(msg)


class AppliedClass:
    def __init__(self, date, start_hour, end_hour, inviter_email):
        self.date = date
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.inviter_email = inviter_email


class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = Flask(__name__)
mail = Mail(app)

# connect to our mongodb
app.config['MONGO_URI'] = "mongodb+srv://nofarana:nofar1234@cluster0-dkcnw.mongodb.net/ClassIt"
app.config['JWT_SECRET_KEY'] = "asdhlkjasnd2234@#$@%@%@$#"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mongo = PyMongo(app)
app.json_encoder = JSONEncoder

value = []
apply_for_class_info = ""
name_of_institution_just_register = ""

user_collection = mongo.db.myusers
rooms_collection = mongo.db.rooms
institutions_collection = mongo.db.institutions
room_application_collection = mongo.db.roomApplication
contact_collection = mongo.db.contact

"""rooms_collection.insert_one(
    {"Class Number": 1102,
     "Building Number": 2,
     "Building Name": "Pomento",
     "Institution": "Academic College of Tel-Aviv Yaffo"})"""


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/confirmation.html")
def a():
    return render_template("confirmation.html")


@app.route("/Contact Us.html")
def s():
    return render_template("Contact Us.html")


@app.route("/Home.html")
def d():
    return render_template("Home.html")


@app.route("/login.html")
def f():
    return render_template("login.html")


@app.route("/Messages.html")
def g():
    return render_template("Messages.html")


@app.route("/Order classroom.html")
def h():
    return render_template("Order classroom.html")


@app.route("/profile.html")
def j():
    return render_template("profile.html")


@app.route("/register.html")
def k():
    return render_template("register.html")


@app.route("/about")
def about():
    return "About page"


@app.route("/upload-classes")
def upload():
    return render_template('index.html')


@app.route('/download-class', methods=['GET'])
def return_class():
    return send_file('class.xlsx', as_attachment=True, attachment_filename="class.xlsx")


@app.route('/download-schedule', methods=['GET'])
def return_schedule():
    return send_file('schedule.xlsx', as_attachment=True, attachment_filename="schedule.xlsx")


# registration
@app.route("/register", methods=["POST"])
def register():
    global name_of_institution_just_register
    data = validate_user(request.get_json())
    if data["ok"]:
        content = data['data']
        content["Password"] = flask_bcrypt.generate_password_hash(content["Password"])
        filter = {"Email": content['Email']}
        if user_collection.count_documents(filter):
            return jsonify({"error": "The email " + content['Email'] + " exists!"}), 500
        else:
            user_collection.insert(
                {"Name": content["Name"], "Email": content['Email'], "Phone Number": content["Phone Number"],
                 "Password": content["Password"], "Institution Name": None})
            return jsonify({"result": "User created successfully"}), 200
    else:
        return jsonify({"error": "Invalid parameters: {}".format(data['message'])}), 500


@app.route("/profile", methods=["GET", "POST"])
@jwt_required
def profile():
    current_user = ObjectId(get_jwt_identity())
    if request.method == "GET":
        user = user_collection.find_one({'_id': current_user})
        institution = user["Institution Name"]
        if institution is None:
            return jsonify({"Name": user["Name"], "Email": user["Email"], "Phone Number": user["Phone Number"], \
                            "Institution Name": None})
        else:
            institution_col = institutions_collection.find_one({'Institution Name': institution})
            return jsonify(
                {"Name": user["Name"], "Email": user["Email"], "Phone Number": user["Phone Number"], "Street": \
                    institution_col["Street"], "City": institution_col["City"],
                 "Institution Name": user["Institution Name"]})
    elif request.method == "POST":
        data = validate_profile(request.get_json())
        if data["ok"]:
            content = data['data']
            user = user_collection.find_one({'_id': current_user})
            administrator_name = user["Name"]
            user_collection.update({"_id": current_user}, {"$set": {"Institution Name": content["Institution Name"]}})
            institutions_collection.insert(
                {"Institution Name": content["Institution Name"], "Street": content["Street"], "City": content["City"], \
                 "Administrator": administrator_name})
            return jsonify({"result": "The institution's details were added successfully"}), 200
        else:
            return jsonify({"error": "Invalid parameters: {}".format(data['message'])}), 500


# uploading the excel file of the class
@app.route("/upload-file", methods=["POST"])
@jwt_required
def upload_file():
    current_user = ObjectId(get_jwt_identity())
    institution_name = user_collection.find_one({'_id': current_user})["Institution Name"]
    if request.method == "POST":
        file = request.files["upload-file"].read()
        file2 = request.files["upload-file2"].read()
        loc = file
        wb = xlrd.open_workbook(file_contents=loc)
        sheet = wb.sheet_by_index(0)
        for i in range(1, sheet.nrows):
            student_seat = True if sheet.cell_value(i, 6) == "כן" else False
            projector = True if sheet.cell_value(i, 7) == "כן" else False
            accessibility = True if sheet.cell_value(i, 8) == "כן" else False
            computers = True if sheet.cell_value(i, 9) == "כן" else False
            rooms_collection.insert_one(
                {"Institution Name": institution_name, "Building Number": int(sheet.cell_value(i, 0)),
                 "Building Name": sheet.cell_value(i, 1),
                 "Floor Number": int(sheet.cell_value(i, 2)), "Class Number": int(sheet.cell_value(i, 3)),
                 "Class Code": str(int(sheet.cell_value(i, 4))),
                 "Number of Seats": int(sheet.cell_value(i, 5)), "Student Seat": student_seat,
                 "Projector": projector, "Accessibility": accessibility,
                 "Computers": computers, "IsApplied": []})
        wb = xlrd.open_workbook(file_contents=file2)
        sheet2 = wb.sheet_by_index(0)
        read_from_file2(sheet2, wb)
        return jsonify({"result": "The file uploaded successfully"}), 200


def read_from_file2(file, book):
    for i in range(1, file.nrows):
        class_code = str(int(file.cell_value(i, 10)))
        date = int(file.cell_value(i, 6))
        dt = Dtime.fromordinal(Dtime(1900, 1, 1).toordinal() + date - 2)
        date = str(dt.date())
        start_hour = file.cell_value(i, 8)
        date_values = xlrd.xldate_as_tuple(start_hour, book.datemode)
        start_hour = my_time(*date_values[3:])
        end_hour = file.cell_value(i, 9)
        date_values = xlrd.xldate_as_tuple(end_hour, book.datemode)
        end_hour = my_time(*date_values[3:])
        applied_obj = AppliedClass(date, str(start_hour)[:5], str(end_hour)[:5], "")
        jsonStr = json.dumps(applied_obj.__dict__)
        print(jsonStr)
        print(rooms_collection.find_one({"Class Code": class_code}))
        rooms_collection.update_one({"Class Code": class_code}, {'$push': {'IsApplied': jsonStr}})


# login the website
@app.route("/login", methods=["POST"])
def login():
    data = validate_login(request.get_json())
    if data['ok']:
        data = data['data']
        user = user_collection.find_one({'Email': data['Email']})
        if user and flask_bcrypt.check_password_hash(user['Password'], data['Password']):
            del user['Password']
            access_token = create_access_token(identity=user['_id'])
            print(access_token)
            return jsonify({'ok': True, 'data': access_token}), 200
        else:
            return jsonify({'ok': False, 'message': 'invalid email or password'}), 401
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


# applied for class form
@app.route("/applying-for-room", methods=['GET', 'POST'])
def apply_for_rooms():
    global value, apply_for_class_info
    is_available = []
    num_of_available = []
    if request.method == "GET":
        institutions_as_json = search_institutions_result()
        return institutions_as_json
    elif request.method == "POST":
        data = validate_apply_for_room(request.get_json())
        if data["ok"]:
            data = data["data"]
            buildings = []
            number_of_classes = data["Number of Classes"]
            num_of_classes = number_of_classes
            count = 0
            while num_of_classes:
                is_available.append(check_if_room_available(data, is_available))
                num_of_classes = (num_of_classes - 1)
            if is_available:
                for x in is_available:
                    if x == "No available room" or x is None:
                        count = (count + 1)
                    elif x is False:
                        return jsonify({'ok': False, 'data': 'institution not found'}), 400
                    else:
                        num_of_available.append(x)
                if count == number_of_classes:
                    return jsonify({'ok': False, 'data': "There is no available room according your requirements"}), 400
                data["IsApproved"] = None
                value = num_of_available
                apply_for_class_info = data
                institution = data["Institution Name"]
                administrator_name = user_collection.find_one({"Institution Name": institution})
                administrator_email = administrator_name["Email"]
                administrator_name = administrator_name["Name"]
                apply_for_class_info.update({"Manger Name": administrator_name})
                class_code = get_class_code(value)
                for classes in class_code:
                    building_name = rooms_collection.find_one({"Class Code": classes})
                    building_name = building_name["Building Name"]
                    buildings.append(building_name)
                # apply_for_class_info.update({"Class code": class_code})
                apply_for_class_info.update({"Number of available classes": len(num_of_available)})
                data["Class Code"] = class_code
                data["Building Name"] = buildings
                room_application_collection.insert_one(data)
                send_email_request(administrator_email, administrator_name)
                return apply_for_class_info
            else:
                return jsonify({'ok': False, 'data': "There is no available room according your requirements"}), 400
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


# get the class's code
def get_class_code(class_id):
    class_code = []
    for classes in class_id:
        exact_class = rooms_collection.find_one({'_id': classes})
        class_code.append(exact_class["Class Code"])
    return class_code


@app.route("/confirmation", methods=["GET", "POST"])
@jwt_required
def getData():
    current_user = ObjectId(get_jwt_identity())
    if request.method == "GET":
        institution_name = user_collection.find_one({'_id': current_user})
        institution_name = institution_name["Institution Name"]
        application = search_messages_result(institution_name)
        return application
    elif request.method == "POST":
        data = validate_confirmation(request.get_json())
        if data["ok"]:
            data = data["data"]
            ID = data["_id"]
            current_application = room_application_collection.find_one({"_id": ObjectId(ID)})
            class_code = current_application["Class Code"]
            email = current_application["Email"]
            name = current_application["Name"]
            if data["Is confirmed"]:
                room_application_collection.update_one({"_id": ObjectId(ID)}, {"$set": {"IsApproved": True}})
                applied_obj = AppliedClass(current_application["Date"], current_application["Start Hour"], \
                                           current_application["Finish Hour"], current_application["Email"])
                jsonStr = json.dumps(applied_obj.__dict__)
                for classes in class_code:
                    rooms_collection.update_one({"Class Code": classes}, {'$push': {'IsApplied': jsonStr}})
                    remove_application(ID, current_application["Date"], current_application["Start Hour"], \
                                       current_application["Finish Hour"])
                send_email_approve(email, name)
                return jsonify({'ok': True, 'data': "The application was approved"}), 200
            else:
                room_application_collection.update_one({"_id": ObjectId(ID)}, {"$set": {"IsApproved": False}})
                send_email_reject(email, name)
                return jsonify({'ok': True, 'data': "The application wasn't approved"}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


def remove_application(ID, date, start_hour, finish_hour):
    applications = room_application_collection.find({"Date": date})
    for application in applications:
        if ID != str(application["_id"]):
            if (date == application["Date"] and application["Finish Hour"] >= start_hour >= application["Start Hour"]) or \
                    (date == application["Date"] and application["Start Hour"] < finish_hour <= application["Finish Hour"]):
                send_email_reject(application["Email"], application["Name"])
                room_application_collection.delete_one({"_id": application["_id"]})


def search_messages_result(institution_name):
    result_from_collection_application = room_application_collection.find({"Institution Name": institution_name})
    applications = []
    for key, inst in enumerate(result_from_collection_application):
        applications.append({str(key): inst})
    return jsonify(results=applications)


def send_email_approve(email, name):
    msg = EmailMessage()
    msg['Subject'] = 'ClassIt | New Class Request'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content(
        'Dear ' + name + ',\n\nYour class request has been successfully approved!\n\n ClassIt-\nTHE EASY WAY TO ORDER A CALSSROOM')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


def send_email_reject(email, name):
    msg = EmailMessage()
    msg['Subject'] = 'ClassIt | Class Request'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content('Dear ' + name + ',\n\nYour class request has been rejected. \n\n ClassIt-\nTHE EASY WAY TO ORDER '
                                     'A CLASSROOM')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


def send_email_request(email, name):
    msg = EmailMessage()
    msg['Subject'] = 'ClassIt | Class Request'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content(
        'Dear ' + name + ',\n\nYou have a new class request in your ClassIt mailbox.\n\n ClassIt-\nTHE EASY WAY TO ORDER A CLASSROOM')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


# checking if the class is available and return the id of the free class
def check_if_room_available(data, class_array):
    number_of_seats = data["Number of Seats"]
    is_projector = data["Projector"]
    is_accessibility = data["Accessibility"]
    is_computers = data["Computers"]
    res = rooms_collection.find({"Institution Name": data['Institution Name']})
    if not res:
        return False
    else:
        for room in res:
            is_time_available = check_class_availability(data, room)
            if class_array:
                if ((number_of_seats <= room["Number of Seats"]) and (
                        (is_projector is False) or (is_projector is True and room["Projector"] is True)) and (
                        (is_accessibility is False) or (
                        is_accessibility is True and room["Accessibility"] is True)) and (
                        (is_computers is False) or (is_computers is True and room["Computers"] is True)) and \
                        room["_id"] not in class_array and is_time_available):
                    return room["_id"]
            else:
                if ((number_of_seats <= room["Number of Seats"]) and (
                        (is_projector is False) or (is_projector is True and room["Projector"] is True)) and (
                        (is_accessibility is False) or (
                        is_accessibility is True and room["Accessibility"] is True)) and ((is_computers is False) or (
                        is_computers is True and room["Computers"] is True)) and is_time_available):
                    return room["_id"]
                else:
                    return "No available room"
        # else:
        #     return False


# searching which institutions were registered to the website and return an array of the names
def search_institutions_result():
    result_from_collection_institutions = institutions_collection.find()
    institutions = []
    for key, inst in enumerate(result_from_collection_institutions):
        institutions.append({str(key): inst["Institution Name"]})
    return jsonify(results=institutions)


# checks the time the class is available
def check_class_availability(data, room):
    date = data["Date"]
    start_hour = data["Start Hour"]
    end_hour = data["Finish Hour"]
    for time in room["IsApplied"]:
        time = json.loads(time)
        if (date == time["date"] and time["end_hour"] >= start_hour >= time["start_hour"]) or \
                (date == time["date"] and time["start_hour"] < end_hour <= time["end_hour"]):
            return False
        else:
            return True
    if not room["IsApplied"]:
        return True


@app.route("/contact", methods=["POST"])
def contact():
    data = validate_contact_request(request.get_json())
    if data["ok"]:
        contact_collection.insert_one(data["data"])
        return jsonify({"result": "contact message created successfully"}), 200
    else:
        return jsonify({"error": "Invalid parameters: {}".format(data['message'])}), 500


# @app.route("/mail-box", methods=["GET", "POST"])
# @jwt_required
# def get_class_applications():
#     current_user = ObjectId(get_jwt_identity())
#     if request.method == "GET":
#         institution_name = user_collection.find_one({'_id': current_user})
#         institution_name = institution_name["Institution Name"]
#         application = room_application_collection.find_one({'Institution': institution_name})
#         return jsonify(application)


if __name__ == '__main__':
    app.run(debug=True)
