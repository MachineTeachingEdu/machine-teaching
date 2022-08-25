from dataclasses import dataclass
from locust import HttpUser, between, task
from mocks.mocked_solution import solution
from os import getenv

@dataclass
class Config:
    id_da_disciplina  = "132" # Comp1_2022_1_Ep(Carla)  sWb-qsF-SDg
    student_login = getenv("STUDENT_EMAIL")
    student_password = getenv("STUDENT_PASSWORD")
    professor_login = getenv("PROFESSOR_EMAIL")
    professor_password = getenv("PROFESSOR_PASSWORD")

class StudentUser(HttpUser):
    host = "https://machine-teaching-app-r22grtpmzq-uc.a.run.app/"
    wait_time = between(1, 3)

    def on_start(self):
        self.login()
        self.wait()

    def on_stop(self):
        self.logout()

    def login(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": "__zlcmid=1ADkxay3bCMr8Cs; csrftoken=z6IRkR64aWVhRd1HPGZmyjZQkhFkWLumZ2WnjuNqZ01np5bNYiSTuJDqgNqMx4sk",
            "Referer": f"{self.host}/en/accounts/login/?next=/en/start",
            "Referrer-Policy": "same-origin"
        }
        
        csrfmiddlewaretoken = "0fyPWcb5X2qyrnghWVECAzLXAxaU42rwqbMlVPSrM6wEZfqn5xx9wZpxw3VmFlpu"

        response = self.client.post(f"{self.host}/en/accounts/login/",
            data=f"csrfmiddlewaretoken={csrfmiddlewaretoken}&username={Config.student_login}&password={Config.student_password}",
            headers=headers, allow_redirects=False)

        self.student_cookies = response.cookies.get_dict()

        response = self.client.post(f"{self.host}/en/accounts/login/",
            data=f"csrfmiddlewaretoken={csrfmiddlewaretoken}&username={Config.professor_login}&password={Config.professor_password}",
            headers=headers, allow_redirects=False)

        self.professor_cookies = response.cookies.get_dict()


    def logout(self):
        response = self.client.get("accounts/logout", cookies=self.student_cookies)
        response = self.client.get("accounts/logout", cookies=self.professor_cookies)
        print("Logout status code:", response.status_code)

    @task
    def post_solution(self):
        solution['csrfmiddlewaretoken'] = self.student_cookies["csrftoken"]
        response = self.client.post("savelog", data=solution, cookies=self.student_cookies)
        print("Solution submission status code:", response.status_code)

    @task
    def test_outcomes(self):
        response = self.client.get(f"outcomes", cookies=self.professor_cookies)
        print("Outcomes status code:", response.status_code)

    @task
    def test_student_dashboard(self):
        response = self.client.get(f"dashboard", cookies=self.student_cookies)
        print("Student dashboard status code:", response.status_code)

    @task
    def test_past_problems(self):
        response = self.client.get(f"past_problems", cookies=self.student_cookies)
        print("past_problems status code:", response.status_code)

    @task   
    def test_class_dashboard(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
            "cookie": f"__zlcmid=1ADkxay3bCMr8Cs;csrftoken={self.professor_cookies['csrftoken']};sessionid={self.professor_cookies['sessionid']}",
        }
        response = self.client.get(self.host + f"en/classes/dashboard/{Config.id_da_disciplina}", headers=headers)
        print("Class dashboard status code:", response.status_code)
