import pymongo
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import json
from schemas import validate_user, validate_login, validate_search_institutions, validate_apply_for_room

app = Flask(__name__)

# connect to our mongodb
app.config['MONGO_URI'] = "mongodb+srv://nofarana:nofar1234@cluster0-dkcnw.mongodb.net/ClassIt"
mongo = PyMongo(app)

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
    return "Main web site"


@app.route("/about")
def about():
    return "About info"


@app.route("/register", methods=["POST"])
def register():
    data = validate_user(request.get_json())
    if data["ok"]:
        content = data['data']
        password = content["Password"]
        filter = {"Email": content['Email']}
        if user_collection.count_documents(filter):
            return jsonify({"error": "The email " + content['Email'] + " exists!"}), 500
        else:
            user_collection.insert_one(data["data"])
            return jsonify({"result": "User created successfully"}), 200
    else:
        return jsonify({"error": "Invalid parameters: {}".format(data['message'])}), 500


@app.route("/login", methods=["POST"])
def login():
    data = validate_login(request.get_json())
    if data['ok']:
        data = data['data']
        user = user_collection.find_one({'Email': data['Email']})
        if user and data['Password']:
            return jsonify({'ok': True, 'data': data['Message']}), 200
        else:
            return jsonify({'ok': False, 'message': 'invalid username or password'}), 401
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


@app.route("/RegistrationForm", methods=['GET', 'POST'])
def apply_for_rooms():
    institutions_as_json = search_institutions_result()
    return institutions_as_json  # TODO need to return the array
    data = validate_apply_for_room(request.get_json())
    if data["ok"]:
        data = data["data"]
        is_available = check_if_room_available(data)
        # room_application_collection.insert_one(data)
        return "OK" if is_available else "NOT AVAILABLE"
    else:
        return "ERROR"


def check_if_room_available(data):
    number_of_seats = data["Number of Seats"]
    is_projector = data["Projector"]
    is_accessability = data["Accessability"]
    res = rooms_collection.find({"Institution": data['Institution']})
    if not res:
        return False
    else:
        for room in res:
            if (number_of_seats <= room["Number of Seats"]) and (is_projector is room["Projector"]) and (
                    is_accessability is room[
                "Accessability"]) \
                    and room["IsApplied"] is False:
                return True
        else:
            return False


def search_institutions_result():
    result_from_collection_institutions = institutions_collection.find()
    institutions = []
    for key, inst in enumerate(result_from_collection_institutions):
        institutions.append({str(key): inst["Institution"]})
    return jsonify(results=institutions)


if __name__ == '__main__':
    app.run(debug=True)
