from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db,ma
import werkzeug

from src.models.user import User, user_schema, users_schema

users = Blueprint("users",__name__,url_prefix="/api/v1/users")

@users.get("/")
def read_all():
 users = User.query.order_by(User.name).all()
 return {"data": users_schema.dump(users)}, HTTPStatus.OK

@users.get("/<int:cedula>")
def read_one(cedula):
    user = User.query.filter_by(cedula=cedula).first()

    if(not user):
        return {"error":"Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data":user_schema.dump(user)},HTTPStatus.OK

@users.post("/")
def create():
    post_data = None
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error":"Posr body JSON data not found","message":str(e)},HTTPStatus.BAD_REQUEST

    user = User(cedula = request.get_json().get("cedula",None),
                nombre = request.get_json().get("nombre",None),
                apellido = request.get_json().get("apellido",None),
                email = request.get_json().get("email",None),
                password = request.get_json().get("password",None))

    try:
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values","message":str(e)},HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)},HTTPStatus.CREATED

@users.patch('/<int:cedula>')
@users.put('/<int:cedula>')
def update(cedula):
    post_data=None

    try:
        post_data=request.get_json()

    except werkzeug.exceptions.BadRequest as e:
        return {"error":"Post body JSON data not found",
                "message":str(e)}, HTTPStatus.BAD_REQUEST

    user=User.query.filter_by(cedula=cedula).first()

    if(not user):
        return {"error":"Resource not found"}, HTTPStatus.NOT_FOUND

    user.nombre=request.get_json().get("name", user.nombre)
    user.apellido=request.get_json().get("apellido", user.apellido)
    user.email=request.get_json().get("email", user.email)
    user.password=request.get_json().get("password", user.password)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values",
                "message":str(e)}, HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)}, HTTPStatus.OK

@users.delete("/<int:cedula>")
def delete(cedula):
    user = User.query.filter_by(cedula=cedula).first()
    if (not user):
        return {"error":"Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values","message":str(e)},HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)},HTTPStatus.NO_CONTENT
#Proveedores de un producto
''' @users.get("/<int:id_user>/providers")
def read_providers(id):
    pass '''