from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db,ma
import werkzeug

from src.models.user import User, user_schema, users_schema
from src.models.ingreso import Ingreso, ingresos_schema
from src.models.egreso import Egreso, egresos_schema

from flask_jwt_extended import jwt_required,get_jwt_identity

users = Blueprint("users",__name__,url_prefix="/api/v1/users")

@users.get("/list")
def read_all():
 users = User.query.order_by(User.cedula).all()
 return {"data": users_schema.dump(users)}, HTTPStatus.OK


@users.get("/")
@jwt_required()
def read_user():
    user = User.query.filter_by(cedula=get_jwt_identity()).first()

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

@users.put('/')
@jwt_required()
def update():
    post_data=None

    try:
        post_data=request.get_json()

    except werkzeug.exceptions.BadRequest as e:
        return {"error":"Post body JSON data not found",
                "message":str(e)}, HTTPStatus.BAD_REQUEST

    user=User.query.filter_by(cedula=get_jwt_identity()).first()

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

@users.delete("/")
@jwt_required()
def delete():
    user = User.query.filter_by(cedula=get_jwt_identity()).first()
    if (not user):
        return {"error":"Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values","message":str(e)},HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)},HTTPStatus.NO_CONTENT

@users.get("/balance")
@jwt_required()
def Balance():
    user=read_user()[0]['data']
    user_cedula=user['cedula']
    egresos = Egreso.query.filter(Egreso.user_cc == user_cedula).all()
    ingresos = Ingreso.query.filter(Ingreso.user_cc == user_cedula).all()
    total_egresos = sum(egr.value for egr in egresos)
    total_ingresos = sum(ing.value for ing in ingresos)

    balance = total_ingresos - total_egresos

    return {"El total de ingresos es: ":total_ingresos, "El total de es egresos es:" :total_egresos,
            "El balance general es": balance}