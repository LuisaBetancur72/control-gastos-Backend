from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.models.egreso import Egreso, egreso_schema, egresos_schema
 
egresos = Blueprint("egresos", __name__, url_prefix="/api/v1/egresos")

@egresos.get("/")
def read_all():
    egresos = Egreso.query.order_by(Egreso.id).all()
    return {"data": egresos_schema.dump(egresos)}, HTTPStatus.OK

@egresos.get("/user")
@jwt_required()
def read_all_egr(user_cc):
    egresos = Egreso.query.filter_by(user_cc=get_jwt_identity()).all()

    if not egresos:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": egresos_schema.dump(egresos)}, HTTPStatus.OK

@egresos.post("/")
@jwt_required()
def create():
    post_data = None
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST
    
    fecha_request = request.get_json().get("fecha", None)
    fecha_date = datetime.strptime(fecha_request, '%Y-%m-%d').date()

    egreso = Egreso(valor=request.get_json().get("valor", None),
                    fecha=fecha_date,
                    descripcion=request.get_json().get("descripcion", None),
                    user_cc=request.get_json().get("user_cc", None))

    try:
        db.session.add(egreso)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": egreso_schema.dump(egreso)}, HTTPStatus.CREATED


@egresos.put('/<int:id>')
@jwt_required()
def update(id):
    post_data = None

    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    egreso = Egreso.query.filter_by(id=id).first()

    if not egreso:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND
    
    fecha_request = request.get_json().get("fecha", None)
    fecha_date = datetime.strptime(fecha_request, '%Y-%m-%d').date()

    egreso.valor = request.get_json().get("valor", egreso.valor)
    egreso.fecha = fecha_date,
    egreso.descripcion = request.get_json().get("descripcion", egreso.descripcion)
    egreso.user_cc = request.get_json().get("user_cc", egreso.user_cc)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": egreso_schema.dump(egreso)}, HTTPStatus.OK

@egresos.delete("/<int:id>")
@jwt_required()
def delete(id):
    egreso = Egreso.query.filter_by(id=id).first()

    if not egreso:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND
    try:
        db.session.delete(egreso)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": egreso_schema.dump(egreso)}, HTTPStatus.NO_CONTENT


@egresos.get("/user/fecha")
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

    egresos = Egreso.query.filter_by(user_cc=get_jwt_identity()).filter(Egreso.fecha >= fecha_inicio, Egreso.fecha <= fecha_fin).all()
        
    return {"data": egresos_schema.dump(egresos)}, HTTPStatus.OK

