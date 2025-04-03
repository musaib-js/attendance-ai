from flask import Flask, request, jsonify
from flask_cors import CORS
from database.models import Attendance, Employee, Team, db
from datetime import datetime
from genai.summarise import summarise_attendance_data
from genai.get_data import generate_sql_query
from flask_restx import Api, Resource
from request_validators import register_models
import logging
from sqlalchemy import text
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


app.config["SQLALCHEMY_DATABASE_URI"] = (
    str(os.getenv("PSQL_URL"))
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

api = Api(app, version="1.0", title="Attendance API", description="AI Enhanced Attendance Platform API")
clock_in_model, clock_out_model, attendance_summary_model,  team_model, employee_model = register_models(api)

db.init_app(app)


@api.route("/api/clock-in")
class AttendanceCreate(Resource):
    @api.expect(clock_in_model)
    def post(self):
        try:
            data = request.json
            employee_id = data.get("employee_id", None)
            work_mode = data.get("work_mode", None)


            # Check if the employee exists
            employee = Employee.query.filter_by(id=employee_id).first()
            if not employee:
                return {"error": "Employee not found"}, 404

            attendance_today = Attendance.query.filter_by(
                date=datetime.now().date(), employee_id=employee_id
            ).first()

            if attendance_today:
                return {"error": "Already clocked in today"}, 400

            try:
                attendance = Attendance(
                    date=datetime.now().date(),
                    clock_in_time=datetime.now().time(),
                    employee_id=employee_id,
                    work_mode=work_mode,
                )
                db.session.add(attendance)
                db.session.commit()
            except Exception as e:
                for x in range(2):
                    try:
                        db.session.commit()
                        break
                    except Exception as e:
                        db.session.rollback()
                        if x == 1:
                            return (
                                    {
                                        "error": "Failed to record attendance. Please contact the HR department to mark your attendance manually. Meanwhile the team is working on it to resolve the issue as soon as possible"
                                    }
                                
                               
                            ), 500

            return {"message": "Clock-in successful"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


@api.route("/api/clock-out")
class AttendanceUpdate(Resource):
    @api.expect(clock_out_model)
    def put(self):
        try:
            data = request.json
            employee_id = data.get("employee_id", None)

            if not employee_id:
                return {"error": "Missing employee_id"}, 400

            employee = Employee.query.filter_by(id=employee_id).first()
            if not employee:
                return {"error": "Employee not found"}, 404

            attendance_today = Attendance.query.filter_by(
                date=datetime.now().date(), employee_id=employee_id
            ).first()

            if not attendance_today:
                return {"error": "Not clocked in today"}, 400

            if attendance_today.clock_out_time is not None:
                return {"error": "Already clocked out today"}, 400

            try:
                attendance_today.clock_out_time = datetime.now().time()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return (
                    (
                        {
                            "error": "Failed to record attendance. Please contact the HR department to mark your attendance manually. Meanwhile the team is working on it to resolve the issue as soon as possible"
                        }
                    ),
                ), 500

            return {"message": "Clock-out successful"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


def clean_response(sql_query):
    """ Remove Markdown-style code blocks from SQL queries. """
    return re.sub(r"```(sql)?\n|\n```", "", sql_query).strip()

@api.route("/api/attendance-summary")
class AttendanceSummary(Resource):
    @api.expect(attendance_summary_model)
    def post(self):
        try:
            data = request.json
            question = data.get("question", None)

            if not question:
                return {"error": "Missing question"}, 400

            sql_query = generate_sql_query(question)
            
            logging.info(f"Generated SQL Query: {sql_query}")
            
            sql_query = clean_response(sql_query)
            
            if not sql_query:
                return {"error": "Failed to generate SQL query"}, 400
            
            result = db.session.execute(text(sql_query)).fetchall()
            
            if not result:
                return {"error": "No data found"}, 404
            
            json_data = [dict(row._mapping) for row in result]

            summary = summarise_attendance_data(question, json_data)
            summary = clean_response(summary)
            logging.info(f"Generated Summary: {summary}")
            
            if not summary:
                return jsonify({"error": "Failed to generate summary"}), 400

            return {"summary": summary}, 200
        except Exception as e:
            return {"error": str(e)}, 500
        
        
        

@api.route("/api/create-team")
class CreateTeam(Resource):
    @api.expect(team_model)
    def post(self):
        try:
            data = request.json
            team_name = data.get("team_name", None)

            if not team_name:
                return {"error": "Missing team_name"}, 400

            existing_team = Team.query.filter_by(team_name=team_name).first()
            if existing_team:
                return {"error": "Team already exists"}, 400

            team = Team(team_name=team_name)
            db.session.add(team)
            db.session.commit()

            return {"message": "Team created successfully", "team_id": team.id}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


@api.route("/api/create-employee")
class CreateEmployee(Resource):
    @api.expect(employee_model)
    def post(self):
        try:
            data = request.json
            name = data.get("name", None)
            role = data.get("role", None)
            team_id = data.get("team_id", None)
            is_manager = data.get("is_manager", False)

            if not name or not role or not team_id:
                return {"error": "Missing required fields (name, role, team_id)"}, 400

            team = Team.query.filter_by(id=team_id).first()
            if not team:
                return {"error": "Team not found"}, 404

            employee = Employee(
                name=name,
                role=role,
                team_id=team_id,
                is_manager=is_manager,
            )
            db.session.add(employee)
            db.session.commit()

            return {"message": "Employee created successfully", "employee_id": employee.id}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


if __name__ == "__main__":
    with app.app_context():

        db.drop_all()

        db.create_all()
        
        # Create sample data like two teams, 10 employees
        team1 = Team(team_name="Team Alpha")
        team2 = Team(team_name="Team Beta")
        db.session.add(team1)
        db.session.add(team2)
        
        db.session.commit()
        
        team1_id = Team.query.filter_by(team_name="Team Alpha").first().id
        team2_id = Team.query.filter_by(team_name="Team Beta").first().id
        
        for i in range(1, 11):
            employee = Employee(
                name =f"Employee {i}",
                role = "Software Engineer",
                team_id = team1_id if i % 2 == 0 else team2_id,
                is_manager = False,
            )
        db.session.add(employee)
        
        db.session.commit()

        print("Database and tables created successfully.")
    app.run(host="0.0.0.0", debug=True, port=5001)
