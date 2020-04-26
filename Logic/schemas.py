from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

user_schema = {
  "type": "object",
  "properties": {
    "Name": {
        "type": "string"
    },
    "Email": {
        "type": "string",
        "format": "email"
    },
    "Phone Number": {
        "type": "string"
    },
    "Password": {
        "type": "string",
        "minLength": 8
    },
    "Institution Name": {
        "type": "string"
    },
    "City": {
        "type": "string"
    },
    "Street": {
        "type": "string"
    },
    "Street Number": {
        "type": "number"
    },
  },
  "required": [
    "Name",
    "Email",
    "Phone Number",
    "Password",
    "Institution Name",
    "City",
    "Street",
    "Street Number"
  ],
    "additionalProperties": False
}

login_schema = {
  "type": "object",
  "properties": {
    "Email": {
        "type": "string",
        "format": "email"
    },
    "Password": {
        "type": "string",
        "minLength": 8
    },
  },
  "required": [
    "Email",
    "Password"
  ],
    "additionalProperties": False
}

search_institution_schema = {
    "type": "object",
    "properties": {
        "Institution": {
            "type": "string"
         },
    },
    "required": [
        "Institution"
    ],
    "additionalProperties": False
}

apply_for_rooms_schema = {
    "type": "object",
    "properties": {
        "Name": {
            "type": "string"
        },
        "Email": {
            "type": "string",
        },
        "Phone Number": {
            "type": "string"
        },
        "Date": {
            "type": "string"
        },
        "Start Hour": {
            "type": "string"
        },
        "Finish Hour": {
            "type": "string"
        },
        "Number of Classes": {
            "type": "number"
        },
        "Number of Seats": {
            "type": "number"
        },
        "Projector": {
            "type": "boolean"
        },
        "Accessibility": {
            "type": "boolean"
        },
        "Institution": {
            "type": "string"
        }
    },
    "required": [
        "Name",
        "Email",
        "Phone Number",
        "Date",
        "Start Hour",
        "Finish Hour",
        "Number of Classes",
        "Number of Seats",
        "Projector",
        "Accessibility",
        "Institution"
    ],
    "additionalProperties": False
}

confirmation_schema = {
    "type": "object",
    "properties": {
        "Is confirmed": {
            "type": "boolean"
         },
        "Class Code": {
            "type": "string"
        },
        "Email of Applier": {
            "type": "string"
        },
        "Date": {
            "type": "string"
        },
        "Start Hour": {
            "type": "string"
        },
        "Finish Hour": {
            "type": "string"
        }
    },
    "required": [
        "Is confirmed",
        "Class Code",
        "Email of Applier",
        "Date",
        "Start Hour",
        "Finish Hour"
    ],
    "additionalProperties": False
}

def validate_user(data):
    try:
        validate(data, user_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}


def validate_login(data):
    try:
        validate(data, login_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}


def validate_search_institutions(data):
    try:
        validate(data, search_institution_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}


def validate_apply_for_room(data):
    try:
        validate(data, apply_for_rooms_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}


def validate_confirmation(data):
    try:
        validate(data, confirmation_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}