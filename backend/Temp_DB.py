from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test1.db'
db = SQLAlchemy(app)

tz = pytz.timezone('Europe/Paris')


class TimeAndTemp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    temperature = db.Column(db.Float, unique=False, nullable=False)

    def __repr__(self):
        tempstr = "%.1f" % self.temperature
        return "\n<Time: " + tz.localize(self.time).__str__() + " // Temp. = " + tempstr + " °C>"


def RecordTemperature(fTemp):
    T0 = TimeAndTemp(time=db.func.now(), temperature=fTemp)
    db.session.add(T0)
    db.session.commit()
