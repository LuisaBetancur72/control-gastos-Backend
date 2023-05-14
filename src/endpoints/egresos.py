from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from datetime import datetime

from src.models.egreso import Egreso, egreso_schema, egresos_schema
 
egresos = Blueprint("egresos", __name__, url_prefix="/api/v1/egresos")

@egresos.get("/")
def read_all():
    egresos = Egreso.query.order_by(Egreso.id).all()
    return {"data": egresos_schema.dump(egresos)}, HTTPStatus.OK

@egresos.get("/<int:id>")
def read_one(id):
    egreso = Egreso.query.filter_by(id=id).first()

    if not egreso:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": egreso_schema.dump(egreso)}, HTTPStatus.OK

@egresos.post("/")
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

@egresos.patch('/<int:id>')
@egresos.put('/<int:id>')
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


@egresos.get("/user/<int:cedula>/fecha")
def read_by_date_range(cedula):
    fecha = None
    try:
        fecha = request.get_json()
    
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Get body JSON data not found", 
                "message": str(e)}, HTTPStatus.BAD_REQUEST
        
        
    fecha_inicio = request.get_json.get("fecha_inicio", None)
    fecha_fin    = request.get_json.get("fecha_fin",None)

    egresos = Egreso.query.filter_by(cedula=cedula).filter(Egreso.date >= fecha_inicio, Egreso.date <= fecha_fin).all()
        
    return {"data": egresos_schema.dump(egresos)}, HTTPStatus.OK

