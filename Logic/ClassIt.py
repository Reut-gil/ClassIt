import pymongo
from flask import Flask, jsonify, request, render_template, url_for, redirect
from flask_pymongo import PyMongo
import json
from schemas import validate_user, validate_login, validate_search_institutions, validate_apply_for_room, \
    validate_confirmation
import datetime
from bson.objectid import ObjectId
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity)
from flask_bcrypt import Bcrypt
from pyexcel_xls import get_data
import pandas as pd
import xlrd


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
                 "Password": content["Password"], "Institution Name": content["Institution Name"]})
            institutions_collection.insert(
                {"Institution Name": content["Institution Name"], "Street": content["Street"], "City": content["City"],
                 "Street Number": content["Street Number"]})
            name_of_institution_just_register = content["Institution Name"]
            return jsonify({"result": "User created successfully"}), 200
    else:
        return jsonify({"error": "Invalid parameters: {}".format(data['message'])}), 500


# uploading the excel file of the class
@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.form['upload-file']
        loc = file
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
        return "OK"


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
            return jsonify({'ok': False, 'message': 'invalid username or password'}), 401
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


# applied for class form
@app.route("/Applying-for-room", methods=['GET', 'POST'])
def apply_for_rooms():
    global value, apply_for_class_info
    is_available = []
    # institutions_as_json = search_institutions_result()
    # return institutions_as_json  # TODO need to return the array
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
            apply_for_class_info.update({"Manger Name": administrator_name})
            class_code = get_class_code(value)
            apply_for_class_info.update({"Class code": class_code})
            apply_for_class_info.update({"Number of available classes": len(is_available)})
            return apply_for_class_info
        else:
            return "NOT AVAILABLE"
    else:
        return "ERROR"


# get the class's code
def get_class_code(class_id):
    class_code = []
    for classes in class_id:
        exact_class = rooms_collection.find_one({'_id': classes})
        class_code.append(exact_class["Class Code"])
    return class_code


@app.route("/confirmation", methods=["POST"])
# @jwt_required
def getData():
    data = validate_confirmation(request.get_json())
    if data["ok"]:
        data = data["data"]
        class_code = data["Class Code"]
        email = data["Email of Applier"]
        if data["Is confirmed"]:
            rooms_collection.update_one({"Class Code": class_code}, {"$set": {"IsAprroved": True}})
            applied_obj = AppliedClass(data["Date"], data["Start Hour"], data["Finish Hour"], data["Email of Applier"])
            jsonStr = json.dumps(applied_obj.__dict__)
            rooms_collection.update({"Class Code": class_code}, {'$push': {'IsApplied': jsonStr}})
            return "The application was approved"  # TODO need to sent an email confirmation + sms
        else:
            return "The application wasn't approved"


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
                        is_accessibility is room["Accessibility"] and room["_id"] not in class_array and is_time_available):
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
        institutions.append({str(key): inst["Institution"]})
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


if __name__ == '__main__':
    app.run(debug=True)
