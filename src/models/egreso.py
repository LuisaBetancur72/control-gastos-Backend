from datetime import datetime
from src.database import db,ma 
from sqlalchemy.orm import validates
import re
 
 
class Egreso(db.Model):
    id          =db.Column(db.Integer, primary_key=True , autoincrment=True)
    valor        =db.Column(db.double, nullable=False)
    fecha       =db.Column(db.Date, nullable=False)
    descripcion  =db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    user_id     = db.Column(db.String(10),
                            db.Foreingkey('user_id'),
                                onupdate="CASACADE",
                                onupdate="RESTRICT",
                                nullable=False)

    def __init__(self, **fields):
        super().__init__(**fields)

    def __repr__(self) -> str:
        return f"User >>> {self.name}"

    @validates(id)
    def validate_id(self,value):
        if not value:
            raise AssertionError('No id provided')
        if not value.isalnum():
            raise AssertionError('Id value must be alphanumeric')
        if Egreso.query.filter(Egreso.id == value).first():
            raise AssertionError('Id is already in use')

        return value
    
    @validates(valor)
    def validate_price(self, key, value):
        if not value:
            raise AssertionError('No price provided')
        # re.match(r"\d+\.*\d*", str)
        if not re.compile("^[-+]?[0-9]*\.?[0-9]+(e[-+]?[0-9]+)?$", value):
            raise AssertionError('Price value must be a real number')
        if value < 0:
            raise AssertionError('Price must be above greater or equal to $0')

        return value
    
    @validates(fecha)
    def validate_expiration(self, key, value):
        if not value:
            raise value
        if not re.match("[0-9]{1,2}\\-[0-9]{1,2}\\-[0-9]{4}", value):
            raise AssertionError('Provided date is not a real date value')
        expiration = datetime.datetime.strptime(value, "%Y-%m-%d")
        return value

    
    @validates(descripcion)
    def validate_name(self, key, value):
        if not value:
            raise AssertionError('No description provided')
        if not value.isalnum():
            raise AssertionError('description value must be alphanumeric')
        if len(value) < 5 or len(value) > 50:
            raise AssertionError('description must be between 5 and 100 characters')

        return value


class EgresoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Egreso
        include_fk=True

egreso_schema = EgresoSchema()
egresos_schema = EgresoSchema(many=True)