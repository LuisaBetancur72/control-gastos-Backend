from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from datetime import datetime

from src.models.ingreso import Ingreso, ingreso_schema, ingresos_schema

ingresos = Blueprint("ingresos",__name__,url_prefix="/api/v1/ingresos")

@ingresos.get("/")
def read_all():
    ingresos = Ingreso.query.order_by(Ingreso.id).all()
    return {"data": ingresos_schema.dump(ingresos)}, HTTPStatus.OK

@ingresos.get("/<int:id>")
def read_one(id):
    ingreso = Ingreso.query.filter_by(id=id).first()

    if (not ingreso):
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": ingreso_schema.dump(ingreso)}, HTTPStatus.OK

@ingresos.post("/")
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

@ingresos.patch('/<int:id>')
@ingresos.put('/<int:id>')
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


@ingresos.get("/user/<int:cedula>/fecha")
def read_by_date_range(cedula):
    fecha = None
    try:
        fecha = request.get_json()
    
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Get body JSON data not found", 
                "message": str(e)}, HTTPStatus.BAD_REQUEST
        
        
    fecha_inicio = request.get_json.get("fecha_inicio", None)
    fecha_fin    = request.get_json.get("fecha_fin",None)

    ingresos = Ingreso.query.filter_by(cedula=cedula).filter(Ingreso.date >= fecha_inicio, Ingreso.date <= fecha_fin).all()
        
    return {"data": ingresos_schema.dump(ingresos)}, HTTPStatus.OK
