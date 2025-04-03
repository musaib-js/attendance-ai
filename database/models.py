from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    clock_in_time = db.Column(db.Time, nullable=False)
    clock_out_time = db.Column(db.Time, nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    work_mode = db.Column(db.String(10), nullable=False)  # 'WFH' or 'WFO'

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    is_manager = db.Column(db.Boolean, default=False)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    employees = db.relationship('Employee', backref='team', lazy=True)
