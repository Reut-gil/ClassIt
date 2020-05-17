import pymongo
from flask import Flask, jsonify, request, render_template, url_for, redirect
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
    return "Main web"


@app.route("/about")
def about():
    return "About page"


@app.route("/upload-classes")
def upload():
    return render_template('index.html')


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
                 "Password": content["Password"]})
            # institutions_collection.insert(
            #     {"Institution Name": content["Institution Name"], "Street": content["Street"], "City": content["City"],
            #      "Street Number": content["Street Number"]})
            # name_of_institution_just_register = content["Institution Name"]
            return jsonify({"result": "User created successfully"}), 200
    else:
        return jsonify({"error": "Invalid parameters: {}".format(data['message'])}), 500


@app.route("/profile", methods=["GET", "POST"])
@jwt_required
def profile():
    current_user = ObjectId(get_jwt_identity())
    if request.method == "GET":
        user = user_collection.find_one({'_id': current_user})
        return jsonify({"Name": user["Name"], "Email": user["Email"], "Phone Number": user["Phone Number"]})
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
@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.form['upload-file']
        file2 = request.form['upload-file2']
        loc = file
        wb = xlrd.open_workbook(file2)
        sheet2 = wb.sheet_by_index(0)
        read_from_file2(sheet2, wb)
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)
        for i in range(1, sheet.nrows):
            student_seat = True if sheet.cell_value(i, 6) == "כן" else False
            projector = True if sheet.cell_value(i, 7) == "כן" else False
            accessibility = True if sheet.cell_value(i, 8) == "כן" else False
            computers = True if sheet.cell_value(i, 9) == "כן" else False
            rooms_collection.insert_one(
                {"Institution Name": name_of_institution_just_register, "Building Number": int(sheet.cell_value(i, 0)),
                 "Building Name": sheet.cell_value(i, 1),
                 "Floor Number": int(sheet.cell_value(i, 2)), "Class Number": int(sheet.cell_value(i, 3)),
                 "Class Code": sheet.cell_value(i, 4),
                 "Number of Seats": int(sheet.cell_value(i, 5)), "Student Seat": student_seat,
                 "Projector": projector, "Accessibility": accessibility,
                 "Computers": computers, "IsApplied": []})
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
    if request.method == "GET":
        institutions_as_json = search_institutions_result()
        return institutions_as_json
    elif request.method == "POST":
        data = validate_apply_for_room(request.get_json())
        if data["ok"]:
            data = data["data"]
            number_of_classes = data["Number of Classes"]
            count = 0
            while number_of_classes:
                is_available.append(check_if_room_available(data, is_available))
                number_of_classes = (number_of_classes - 1)
            if is_available:
                for x in is_available:
                    if x == "No available room":
                        count = (count + 1)
                    if x is False:
                        return jsonify({'ok': False, 'data': 'institution not found'}), 400
                if count == len(is_available):
                    return jsonify({'ok': False, 'data': "There is no available room according your requirements"}), 400
                is_available.remove("No available room")
                room_application_collection.insert_one(data)
                room_application_collection.update({"Email": data["Email"]}, {"$set": {"IsAprroved": False}})
                value = is_available
                apply_for_class_info = data
                institution = data["Institution"]
                administrator_name = user_collection.find_one({"Institution Name": institution})
                administrator_name = administrator_name["Name"]
                administrator_email = administrator_name["Email"]
                apply_for_class_info.update({"Manger Name": administrator_name})
                class_code = get_class_code(value)
                apply_for_class_info.update({"Class code": class_code})
                apply_for_class_info.update({"Number of available classes": len(is_available)})
                send_email_request(administrator_email)
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


@app.route("/confirmation", methods=["POST"])
@jwt_required
def getData():
    data = validate_confirmation(request.get_json())
    if data["ok"]:
        data = data["data"]
        class_code = data["Class Code"]
        email = data["Email of Applier"]
        if data["Is confirmed"]:
            room_application_collection.update_one({"Class Code": class_code}, {"$set": {"IsAprroved": True}})
            applied_obj = AppliedClass(data["Date"], data["Start Hour"], data["Finish Hour"], data["Email of Applier"])
            jsonStr = json.dumps(applied_obj.__dict__)
            rooms_collection.update({"Class Code": class_code}, {'$push': {'IsApplied': jsonStr}})
            send_email_approve(email)
            return jsonify({'ok': True, 'data': "The application was approved"}), 200  # TODO need to sent an email
            # confirmation + sms
        else:
            send_email_reject(email)
            return jsonify({'ok': True, 'data': "The application wasn't approved"}), 200
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


def send_email_approve(email):
    msg = EmailMessage()
    msg['Subject'] = 'ClassIt | Class Request'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content('Your class request has been successfully approved!')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


def send_email_reject(email):
    msg = EmailMessage()
    msg['Subject'] = 'ClassIt | Class Request'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content('Your class request has been rejected!')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


def send_email_request(email):
    msg = EmailMessage()
    msg['Subject'] = 'ClassIt | Class Request'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content('You have a new class request in your mailbox')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


# checking if the class is available and return the id of the free class
def check_if_room_available(data, class_array):
    number_of_seats = data["Number of Seats"]
    is_projector = data["Projector"]
    is_accessibility = data["Accessibility"]
    res = rooms_collection.find({"Institution": data['Institution']})
    if not res:
        return False
    else:
        for room in res:
            is_time_available = check_class_availability(data, room)
            if class_array:
                if (number_of_seats <= room["Number of Seats"]) and (is_projector is room["Projector"]) and (
                        is_accessibility is room["Accessibility"] and room[
                    "_id"] not in class_array and is_time_available):
                    return room["_id"]
                else:
                    return "No available room"
            else:
                if (number_of_seats <= room["Number of Seats"]) and (is_projector is room["Projector"]) and (
                        is_accessibility is room["Accessibility"] and is_time_available):
                    return room["_id"]
                else:
                    return "No available room"
        else:
            return False


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


@app.route("/contact")
def contact():
    data = validate_contact_request(request.get_json())
    if data["ok"]:
        contact_collection.insert_one(data["data"])
        return jsonify({"result": "contact message created successfully"}), 200
    else:
        return jsonify({"error": "Invalid parameters: {}".format(data['message'])}), 500


@app.route("/mail-box", methods=["GET"])
@jwt_required
def get_class_applications():
    current_user = ObjectId(get_jwt_identity())
    institution_name = user_collection.find_one({'_id': current_user})
    institution_name = institution_name["Institution Name"]
    application = room_application_collection.find_one({'Institution': institution_name})
    return jsonify(application)


if __name__ == '__main__':
    app.run(debug=True)
