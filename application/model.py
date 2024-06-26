from .db import db


class UserModel(db.Document):
    cpf = db.StringField(required=True, unique=True, max_lenght=50)
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    email = db.EmailField(required=True)
    birthday_date = db.DateTimeField(required=True)

class HealthCheckModel(db.Document):
    status = db.StringField()