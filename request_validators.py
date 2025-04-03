from flask_restx import fields, Model

def register_models(api):
    """Registers models with the API"""
    

    clock_in_model = api.model(
        "ClockIn",
        {
            "employee_id": fields.Integer(required=True, description="Employee ID"),
            "work_mode": fields.String(
                required=True, enum=["WFH", "WFO"], description="Work mode (WFH/WFO)"
            ),
        },
    )

    clock_out_model = api.model(
        "ClockOut",
        {
            "employee_id": fields.Integer(required=True, description="Employee ID"),
        },
    )

    attendance_summary_model = api.model(
        "AttendanceSummary",
        {
            "question": fields.String(required=True, description="Natural language query for attendance summary"),
        },
    )
    
    team_model = api.model(
        "Team",
        {
            "team_name": fields.String(required=True, description="Name of the team"),
        },
    )
    employee_model = api.model(
        "Employee",
        {
            "name": fields.String(required=True, description="Name of the employee"),
            "role": fields.String(required=True, description="Role of the employee"),
            "team_id": fields.Integer(required=True, description="Team ID"),
            "is_manager": fields.Boolean(required=False, description="Is the employee a manager"),
        },
    )

    return clock_in_model, clock_out_model, attendance_summary_model, team_model, employee_model
