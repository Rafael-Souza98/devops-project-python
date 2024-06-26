import re
from flask import  jsonify
from flask_restful import  Resource, reqparse
from mongoengine import NotUniqueError
from .model import UserModel, HealthCheckModel



_user_parser = reqparse.RequestParser()
_user_parser.add_argument('first_name', type=str, required=True, help="This field cannot be blank")
_user_parser.add_argument('last_name', type=str, required=True, help="This field cannot be blank")
_user_parser.add_argument('cpf', type=str, required=True, help="This field cannot be blank")
_user_parser.add_argument('email', type=str, required=True, help="This field cannot be blank")
_user_parser.add_argument('birthday_date', type=str, required=True, help="This field cannot be blank")

class HealthCheck(Resource):
    def get(self):
        resp = HealthCheckModel.objects(status="health")
        if resp:
            return "Healthy", 200
        else:
            HealthCheckModel(status="health").save()
            return "Healthy", 200



class Users(Resource):
    def get(self):
        return jsonify(UserModel.objects())

class User(Resource):
    def validate_cpf(self, cpf):
        #Has the correct mask
        
        if not re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
            return False
    
    # Remove todos os caracteres não numéricos do CPF
        cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se o CPF tem 11 dígitos
        if len(cpf) != 11:
            return False

    # Converte os dígitos do CPF em uma lista de inteiros
        numbers = [int(digit) for digit in cpf]

    # Validação do primeiro dígito verificador
        sum_of_products = sum(a * b for a, b in zip(numbers[:9], range(10, 1, -1)))
        expected_digit = (sum_of_products * 10) % 11
        if expected_digit == 10:
            expected_digit = 0
        if numbers[9] != expected_digit:
            return False

    # Validação do segundo dígito verificador
        sum_of_products = sum(a * b for a, b in zip(numbers[:10], range(11, 1, -1)))
        expected_digit = (sum_of_products * 10) % 11
        if expected_digit == 10:
            expected_digit = 0
        if numbers[10] != expected_digit:
            return False

        return True

    def post(self):
        data = _user_parser.parse_args()
        if not self.validate_cpf(cpf=data["cpf"]):
            return {"message": "CPF is invalid!"}, 400
        
        try:
            response = UserModel(**data).save()
            return {"message": "User %s successfully create!" %response.id}
        except NotUniqueError:
            return {"message": "This CPF has been register"}, 400

    def get(self, cpf):
            resp = UserModel.objects(cpf=cpf)
            if resp:
                return jsonify(resp)
            return {"message": "User doesn't exist"}, 400
    
    def patch(self):
        data = _user_parser.parse_args()
        if not self.validate_cpf(cpf=data["cpf"]):
            return {"message": "CPF is invalid!"}, 400
        
        response = UserModel.objects(cpf=data["cpf"])
        if response:
            response.update(**data)
            return {"message": "User updated"}, 200
        else:
            return {"message": "User doesn't exist"}, 400
        
    def delete(self, cpf):
            resp = UserModel.objects(cpf=cpf)

            if resp:
                resp.delete()
                return {"message": "User deleted!"}, 200
            else:
                return {"message": "User doesn't exist"}, 400
