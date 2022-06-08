from locust import HttpUser, between, task
from pyquery import PyQuery

class StudentUser(HttpUser):
    host = "https://machine-teaching-app-r22grtpmzq-uc.a.run.app/"
    wait_time = between(5, 15)

    def on_start(self):
        self.login()
        self.solution = self.fill_form() # after login
        self.wait()

    def on_stop(self):
        self.logout()

    def login(self):
        '''Manages session login for tests'''
        response = self.client.get("accounts/login/")
        pq = PyQuery(response.content)
        csrf  = pq('input:hidden').eq(0).val()
        self.cookies = response.cookies
        self.csrftoken = response.cookies.get("csrftoken")
        login = {}
        login['csrfmiddlewaretoken'] = csrf
        login['username'] = "gabrielxara@gmail.com"
        login['password'] = "senha12341234"
        login['next'] = ""
        response = self.client.post("accounts/login/", data=login, cookies=self.cookies)
        print("Login status code:", response.status_code)
        # ~ html = open('login.html','w+t')
        # ~ print(response.content,file=html)
        # ~ html.close()
        print("cookies[csrftoken]:", response.cookies.get('csrftoken'))
        print("csrftoken:", self.csrftoken)

    def logout(self):
        response = self.client.get("accounts/logout", cookies=self.cookies)
        print("Logout status code:", response.status_code)

    def fill_form(self):
        solution = {}
        solution['problem'] = '802'
        solution['solution'] = "def PosNegZero(x):\n\tif x>0:\n\t\treturn str(x) + \" e positivo\"\n\telif x<0:\n\t\treturn str(x) + \" e negativo\"\n\telse:\n\t\treturn str(x) + \" e zero\""
        solution['outcome'] = 'P'
        solution['seconds_in_code'] = '68'
        solution['seconds_to_begin'] = '80'
        solution['seconds_in_page'] = '198'
        solution['solution_lines'] = '10'
        output = []
        output.extend(["-43 e negativo","-68 e negativo","27 e positivo","77 e positivo","16 e positivo"])
        output.extend(["-75 e negativo","60 e positivo","25 e positivo","31 e positivo","20 e positivo"])
        output.extend(["-51 e negativo","4 e positivo","26 e positivo","-3 e negativo","-20 e negativo"])
        output.extend(["-39 e negativo","0 e zero","25 e positivo","-73 e negativo","-79 e negativo"])
        output.extend(["-70 e negativo","55 e positivo","3 e positivo","74 e positivo","54 e positivo"])
        output.extend(["-23 e negativo","-24 e negativo","-7 e negativo","57 e positivo","-41 e negativo"])
        output.extend(["15 e positivo","58 e positivo","-65 e negativo","-14 e negativo","49 e positivo"])
        output.extend(["0 e zero","78 e positivo","57 e positivo","8 e positivo","-9 e negativo","-69 e negativo"])
        output.extend(["-40 e negativo","-11 e negativo","-20 e negativo","-28 e negativo","79 e positivo"])
        output.extend(["72 e positivo","-38 e negativo","-76 e negativo","-50 e negativo","9 e positivo"])
        solution['console'] = '\n'.join(output)
        solution['csrfmiddlewaretoken'] = self.csrftoken
        return solution

    @task
    def post_solution(self):
        response = self.client.post("savelog", data=self.solution, cookies=self.cookies)
        print(response.text)
        print("Solution submission status code:", response.status_code)
        # ~ html = open('post.html','w+t')
        # ~ print(response.content,file=html)
        # ~ html.close()




## Campos para preencher na tela de savelog:
## Testar também com a classes/dashboard/{id_da_turma}
## Testar também com a student_dashboard/{id_do_aluno}

    # OUTCOMES = (("F", "Failed"), ("P", "Passed"), ("S", "Skipped"))
    # ERROR_TYPE = (("C", "Conceptual"), ("S", "Syntax"), ("D", "Distraction"),  ("I", "Interpretation"))

    # problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    # solution = models.TextField(blank=True)
    # outcome = models.CharField(max_length=2, choices=OUTCOMES)
    # console = models.TextField(blank=True)
    # seconds_in_code = models.IntegerField()
    # seconds_in_page = models.IntegerField()
    # seconds_to_begin = models.IntegerField()
    # solution_lines = models.IntegerField()
    # test_case_hits = models.IntegerField(blank=True, null=True)