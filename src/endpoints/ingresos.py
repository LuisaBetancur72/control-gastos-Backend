from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from src.models.ingreso import Ingreso, ingreso_schema, ingresos_schema

ingresos = Blueprint("ingresos", __name__, url_prefix="/api/v1/ingresos")

@ingresos.get("/")
def read_all():
    ingresos = Ingreso.query.order_by(Ingreso.fecha).all()
    return {"data": ingresos_schema.dump(ingresos)}, HTTPStatus.OK

@ingresos.get("/<string:id>")
def read_one(id):
    ingreso = Ingreso.query.filter_by(id=id).first()

    if not ingreso:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": ingreso_schema.dump(ingreso)}, HTTPStatus.OK

@ingresos.post("/")
def create():
    post_data = None
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    ingreso = Ingreso(id=request.get_json().get("id", None),
                      valor=request.get_json().get("valor", None),
                      fecha=request.get_json().get("fecha", None),
                      descripcion=request.get_json().get("descripcion", None),
                      user_id=request.get_json().get("user_id", None))

    try:
        db.session.add(ingreso)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": ingreso_schema.dump(ingreso)}, HTTPStatus.CREATED

@ingresos.patch('/<string:id>')
@ingresos.put('/<string:id>')
def update(id):
    post_data = None

    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    ingreso = Ingreso.query.filter_by(id=id).first()

    if not ingreso:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    ingreso.valor = request.get_json().get("valor", ingreso.valor)
    ingreso.fecha = request.get_json().get("fecha", ingreso.fecha)
    ingreso.descripcion = request.get_json().get("descripcion", ingreso.descripcion)
    ingreso.user_id = request.get_json().get("user_id", ingreso.user_id)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST
    return {"data": ingreso_schema.dump(ingreso)}, HTTPStatus.OK

@ingresos.delete("/<string:id>")
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
