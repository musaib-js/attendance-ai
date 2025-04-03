from locust import HttpUser, task, between

class AttendanceUser(HttpUser):
    wait_time = between(1, 2) 

    @task
    def clock_in(self):
        self.client.post("/api/clock-in", json={"employee_id": 7, "work_mode": "WFO"})

    @task
    def clock_out(self):
        self.client.put("/api/clock-out", json={"employee_id": 7})

