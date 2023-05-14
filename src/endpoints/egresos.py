from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from src.models.egreso import Egreso, egreso_schema, egresos_schema
 
egresos = Blueprint("egresos", __name__, url_prefix="/api/v1/egresos")

@egresos.get("/")
def read_all():
    egresos = Egreso.query.order_by(Egreso.fecha).all()
    return {"data": egresos_schema.dump(egresos)}, HTTPStatus.OK

@egresos.get("/<string:id>")
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

    egreso = Egreso(id=request.get_json().get("id", None),
                    valor=request.get_json().get("valor", None),
                    fecha=request.get_json().get("fecha", None),
                    descripcion=request.get_json().get("descripcion", None),
                    user_id=request.get_json().get("user_id", None))

    try:
        db.session.add(egreso)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": egreso_schema.dump(egreso)}, HTTPStatus.CREATED

@egresos.patch('/<string:id>')
@egresos.put('/<string:id>')
def update(id):
    post_data = None

    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    egreso = Egreso.query.filter_by(id=id).first()

    if not egreso:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    egreso.valor = request.get_json().get("valor", egreso.valor)
    egreso.fecha = request.get_json().get("fecha", egreso.fecha)
    egreso.descripcion = request.get_json().get("descripcion", egreso.descripcion)
    egreso.user_id = request.get_json().get("user_id", egreso.user_id)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": egreso_schema.dump(egreso)}, HTTPStatus.OK

@egresos.delete("/<string:id>")
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
