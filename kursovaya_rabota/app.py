from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "db.sqlite3")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

# Ensure database tables exist at startup (avoid relying on removed/changed decorators)
with app.app_context():
    db.create_all()
    # Seed sample data if DB is empty (useful for first run / demo)
    if Production.query.count() == 0:
        sample = [
            Production(title="Ромео и Джульетта", description="Классическая трагедия Шекспира в современной интерпретации", director="Алексей Смирнов", genre="Драма", premiere_date=datetime(2026,2,14,19,0), capacity=250, status='Аншлаг'),
            Production(title="Кукольный мир", description="Семейная постановка для детей", director="Екатерина Ли", genre="Детская", premiere_date=datetime(2026,1,10,12,0), capacity=120, status='Репетиции'),
            Production(title="Эксперимент", description="Современная постановка: экспрессивный театр", director="Марина К.", genre="Авангард", premiere_date=None, capacity=80, status='Подготовка'),
        ]
        db.session.bulk_save_objects(sample)
        db.session.commit()

@app.route('/')
def index():
    q = request.args.get('q', '')
    if q:
        productions = Production.query.filter(Production.title.contains(q)).order_by(Production.premiere_date.asc()).all()
    else:
        productions = Production.query.order_by(Production.premiere_date.asc()).all()
    return render_template('index.html', productions=productions, q=q)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        director = request.form.get('director', '').strip()
        genre = request.form.get('genre', '').strip()
        date_raw = request.form.get('date', '').strip()
        capacity_raw = request.form.get('capacity', '0').strip()
        status = request.form.get('status', 'Подготовка').strip()

        if not title:
            flash('Название обязательно', 'error')
            return redirect(url_for('create'))

        try:
            date = datetime.fromisoformat(date_raw) if date_raw else None
        except ValueError:
            flash('Неверный формат даты. Используйте YYYY-MM-DD или ISO формат.', 'error')
            return redirect(url_for('create'))

        try:
            capacity = int(capacity_raw)
            if capacity < 0:
                raise ValueError()
        except ValueError:
            flash('Вместимость должна быть неотрицательным целым числом', 'error')
            return redirect(url_for('create'))

        prod = Production(title=title, description=description, director=director, genre=genre, premiere_date=date, capacity=capacity, status=status)
        db.session.add(prod)
        db.session.commit()
        flash('Постановка создана', 'success')
        return redirect(url_for('index'))
    return render_template('form.html', action='Создать', production=None)

@app.route('/edit/<int:prod_id>', methods=['GET', 'POST'])
def edit(prod_id):
    prod = Production.query.get_or_404(prod_id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        director = request.form.get('director', '').strip()
        genre = request.form.get('genre', '').strip()
        date_raw = request.form.get('date', '').strip()
        capacity_raw = request.form.get('capacity', '0').strip()
        status = request.form.get('status', 'Подготовка').strip()

        if not title:
            flash('Название обязательно', 'error')
            return redirect(url_for('edit', prod_id=prod_id))

        try:
            date = datetime.fromisoformat(date_raw) if date_raw else None
        except ValueError:
            flash('Неверный формат даты. Используйте YYYY-MM-DD или ISO формат.', 'error')
            return redirect(url_for('edit', prod_id=prod_id))

        try:
            capacity = int(capacity_raw)
            if capacity < 0:
                raise ValueError()
        except ValueError:
            flash('Вместимость должна быть неотрицательным целым числом', 'error')
            return redirect(url_for('edit', prod_id=prod_id))

        prod.title = title
        prod.description = description
        prod.director = director
        prod.genre = genre
        prod.premiere_date = date
        prod.capacity = capacity
        prod.status = status
        db.session.commit()
        flash('Постановка обновлена', 'success')
        return redirect(url_for('index'))

    return render_template('form.html', action='Редактировать', production=prod)

@app.route('/delete/<int:prod_id>', methods=['POST'])
def delete(prod_id):
    prod = Production.query.get_or_404(prod_id)
    db.session.delete(prod)
    db.session.commit()
    flash('Постановка удалена', 'success')
    return redirect(url_for('index'))

@app.route('/detail/<int:prod_id>')
def detail(prod_id):
    prod = Production.query.get_or_404(prod_id)
    return render_template('detail.html', production=prod)

if __name__ == '__main__':
    app.run(debug=True)
