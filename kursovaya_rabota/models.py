from app import db
from datetime import datetime

class Production(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    director = db.Column(db.String(120), nullable=True)
    genre = db.Column(db.String(80), nullable=True)
    premiere_date = db.Column(db.DateTime, nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(40), nullable=False, default='Подготовка')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Production {self.title}>"
