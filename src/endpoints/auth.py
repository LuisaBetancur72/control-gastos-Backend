from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, current_user
from http import HTTPStatus
from src.models.user import User
from src.database import jwt

from src.models.user import User, user_schema, users_schema

auth = Blueprint("auth",
                __name__,
                url_prefix="/api/v1/auth")


@auth.post("/login")
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(cedula=username).one_or_none()
    if not user or not user.check_password(password):
        return {"error": "Wrong username or password"}, HTTPStatus.UNAUTHORIZED
    
    access_token = create_access_token(identity=user_schema.dump(user))
    response = {"access_token": access_token}

    return response, HTTPStatus.OK

@auth.get("/whoami")
@jwt_required()
def who_am_i():
 return {
        "cedula":     current_user.cedula,
        "nombre":     current_user.nombre,
        "apellido":   current_user.apellido,
        "email":      current_user.email,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }, HTTPStatus.OK


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(cedula=identity).one_or_none()
