from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder="static", static_url_path='/static')
app.debug = True
app.config['SECRET_KEY'] = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Data(db.Model):
    __tablename__ = 'data'
    id = Column(INTEGER, primary_key=True)
    datetime = Column(DateTime, nullable=True)
    water_temp_c = Column(REAL(), nullable=False)
    air_temp_c = Column(REAL(), nullable=False)
    humidity = Column(REAL(), nullable=False)
    pump_state = Column(INTEGER, default=False)
    led_state = Column(INTEGER, default=False)
    water_level = Column(INTEGER, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
