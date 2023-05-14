from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity

from src.models.ingreso import Ingreso, ingreso_schema, ingresos_schema

ingresos = Blueprint("ingresos",__name__,url_prefix="/api/v1/ingresos")

@ingresos.get("/")
def read_all():
    ingresos = Ingreso.query.order_by(Ingreso.id).all()
    return {"data": ingresos_schema.dump(ingresos)}, HTTPStatus.OK

@ingresos.get("/user")
@jwt_required()
def read_all_ing():
    ingreso = Ingreso.query.order_by(Ingreso.id).all()

    if (not ingreso):
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": ingreso_schema.dump(ingreso)}, HTTPStatus.OK

@ingresos.post("/")
@jwt_required()
def create():
    post_data = None
    
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST
    fecha_request = request.get_json().get("fecha", None)
    fecha_date = datetime.strptime(fecha_request, '%Y-%m-%d').date()


    ingreso = Ingreso(valor=request.get_json().get("valor", None),
                      fecha=fecha_date,
                      descripcion=request.get_json().get("descripcion", None),
                      user_cc=request.get_json().get("user_cc", None))

    try:
        db.session.add(ingreso)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": ingreso_schema.dump(ingreso)}, HTTPStatus.CREATED


@ingresos.put('/<int:id>')
@jwt_required()
def update(id):
    post_data = None

    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    ingreso = Ingreso.query.filter_by(id=id).first()

    if not ingreso:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    fecha_request = request.get_json().get("fecha", None)
    fecha_date = datetime.strptime(fecha_request, '%Y-%m-%d').date()


    ingreso.valor = request.get_json().get("valor", ingreso.valor)
    ingreso.fecha = request.get_json().get("fecha", ingreso.fecha)
    ingreso.descripcion = fecha_date,
    ingreso.cedula = request.get_json().get("cedula", ingreso.user_cc)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST
    return {"data": ingreso_schema.dump(ingreso)}, HTTPStatus.OK

@ingresos.delete("/<int:id>")
@jwt_required()
def delete(id):
    ingreso = Ingreso.query.filter_by(id=id).first()

    if not ingreso:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(ingreso)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": ingreso_schema.dump(ingreso)}, HTTPStatus.NO_CONTENT


@ingresos.get("/user/fecha")
@jwt_required()
def read_by_date_range():
    fecha = None
    try:
        fecha = request.get_json()
    
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Get body JSON data not found", 
                "message": str(e)}, HTTPStatus.BAD_REQUEST
    
    fecha_request_i = request.get_json().get("fecha_inicio", None)
    fecha_request_f = request.get_json().get("fecha_fin", None)  
        
    fecha_inicio = datetime.strptime(fecha_request_i, '%Y-%m-%d').date()
    fecha_fin    = datetime.strptime(fecha_request_f, '%Y-%m-%d').date()

    ingresos = Ingreso.query.filter_by(user_cc=get_jwt_identity()).filter(Ingreso.fecha >= fecha_inicio, Ingreso.fecha <= fecha_fin).all()
        
    return {"data": ingresos_schema.dump(ingresos)}, HTTPStatus.OK