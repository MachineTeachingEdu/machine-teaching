import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from django.conf import settings
from django.contrib.auth.models import User
from questions.models import Professor, OnlineClass
from django.test.utils import override_settings
from django.db import connection

global USER_CLASS

@override_settings(DEBUG=True)
class DjkSampleTestCase(StaticLiveServerTestCase):
    reset_sequences = False

class InterfaceTests(DjkSampleTestCase):

    @classmethod
    def setUpClass(cls): 
        super().setUpClass() 
        cls.playwright = sync_playwright().start() 
        headless = False     # False to show browser while testing
        cls.browser = cls.playwright.chromium.launch(headless=headless) 
        User.objects.create_superuser(username=settings.TEST_SUPERUSER_USER, email=settings.TEST_SUPERUSER_EMAIL, password=settings.TEST_SUPERUSER_PASSWORD)
 
    @classmethod 
    def tearDownClass(cls): 
        cls.browser.close() 
        cls.playwright.stop() 
        super().tearDownClass() 
    
    def about(self, page):
        page.goto(f"{self.live_server_url}/pt-br")
        page.click('.footer-right span:nth-child(3)')
        #self.assertEqual('About this research', page.locator('text=About this research').text_content())
        self.assertEqual('Sobre a pesquisa', page.locator('text=Sobre a pesquisa').text_content())

    def change_language(self, page):
        page.goto(f"{self.live_server_url}/pt-br")
        page.click('.change-language')
        self.assertEqual('Welcome to  Machine Teaching', page.locator('.landing h1').text_content())
        page.click('.change-language')
        self.assertEqual('Bem-vindo ao Machine Teaching',page.locator('.landing h1').text_content())

    def read_terms(self, page):
        page.goto(f"{self.live_server_url}/pt-br")
        page.click('.footer-right span:nth-child(1)')
        self.assertEqual('Termos e condições', page.locator('.bg2 .card h3').text_content())

    def read_privacy(self, page):
        page.goto(f"{self.live_server_url}/pt-br")
        page.click('.footer-right span:nth-child(2)')
        self.assertEqual('Política de privacidade', page.locator('.bg2 .card h3').text_content())

    def register(self, page, class_code, gname, sname, user, password):
        page.goto(f"{self.live_server_url}/pt-br/signup")
        page.fill('form[action="/pt-br/signup"] input[name="first_name"]', gname)
        page.fill('form[action="/pt-br/signup"] input[name="last_name"]', sname)
        page.fill('form[action="/pt-br/signup"] input[name="email"]', user)
        page.fill('form[action="/pt-br/signup"] input[name="class_code"]', class_code)
        page.fill('form[action="/pt-br/signup"] input[name="university"]', 'UFRJ')
        page.fill('form[action="/pt-br/signup"] input[name="registration"]', '123456789')
        page.locator("#id_course").select_option('Astronomia')
        page.fill('form[action="/pt-br/signup"] input[name="password1"]', password)
        page.fill('form[action="/pt-br/signup"] input[name="password2"]', password)
        page.locator('form[action="/pt-br/signup"] input[name="accepted"]').check()
        page.locator('form[action="/pt-br/signup"] input[name="read"]').check()
        page.click('form[action="/pt-br/signup"] button[type="submit"]')

        self.assertEqual("início", page.locator('.content .topbar-left .title').text_content())

    def login(self, page, user, password):
        page.set_default_timeout(0)
        page.goto(f"{self.live_server_url}/pt-br/accounts/login/?next=/pt-br/start")
        page.fill('form[action="/pt-br/accounts/login/"] input[name="username"]', user)
        page.fill('form[action="/pt-br/accounts/login/"] input[name="password"]', password)
        page.click('form[action="/pt-br/accounts/login/"] button[type="submit"]')
        page.goto(f"{self.live_server_url}/pt-br/start")
        self.assertEqual("início", page.locator('.content .topbar-left .title').text_content())

    ### não está sendo usada
    def next(self, page):
        page.goto(f"{self.live_server_url}/pt-br/next")
        self.assertEqual("Problema", page.locator('.content .topbar-left .title').text_content())
    
    def outcomes(self, page):
        page.goto(f"{self.live_server_url}/pt-br/dashboard")
        self.assertEqual("Problemas", page.locator('.layout-content .col.col-6 .col-7 .card h3').text_content())

    def past_chapters(self, page):
        page.goto(f"{self.live_server_url}/pt-br/past_problems")
        self.assertEqual("Problemas passados", page.locator('.content .topbar-left .title').text_content())

    def chapters(self, page):
        page.goto(f"{self.live_server_url}/pt-br/chapters")
        self.assertEqual("Aulas", page.locator('.content .topbar-left .title').text_content())

    def specific_chapter(self, page):
        page.goto(f"{self.live_server_url}/pt-br/chapters/1")
        self.assertEqual("Problemas", page.locator('.layout-content .col.col-7 .card.chapter-list h3').text_content())
    
    def specific_problem(self, page):
        page.goto(f"{self.live_server_url}/pt-br/chapters/1")
        self.assertEqual("Progresso", page.locator('text=Progresso').text_content())
    
    def specific_problem_2(self, page):
        page.goto(f"{self.live_server_url}/pt-br/chapters/1")
        self.assertEqual("Data de entrega", page.locator('text=Entrega').text_content())

    def past_solutions(self, page):
        page.goto(f"{self.live_server_url}/pt-br/problem_solutions/1")
        self.assertEqual("Problema atual", page.locator('text=Problema atual').text_content())

    def create_professor(self, page):
        page.goto(f"{self.live_server_url}/pt-br/admin/")
        page.fill('#id_username', settings.TEST_SUPERUSER_EMAIL)
        page.fill('#id_password', settings.TEST_SUPERUSER_PASSWORD)
        page.click('input[type="submit"]')
        page.click('text=Grupos')
        page.click('text=Adicionar grupo')
        page.fill('#id_name', 'Professor')
        page.click('text=Escolher todos')
        page.click('text=Salvar')
        Professor.objects.create(user=User.objects.get(username=settings.TEST_MANAGER))
  
    def assign_exercise(self, page):
        page.goto(f"{self.live_server_url}/pt-br/classes/manage/2")
        page.fill('input[type="date"]', '2022-12-12')
        page.fill('input[name="time"]', '23:59')
        page.click('text=Adicionar')     

    def exercise(self, page):
        page.goto(f"{self.live_server_url}/pt-br/1")
        self.assertEqual("Exercicio_Teste", page.locator('text=Exercicio_Teste Pular >> h3').text_content())
        self.write_code(page)
        self.assertEqual("Casos de teste", page.locator('text=Casos de teste').text_content())
        self.write_terminal(page)
        self.assertEqual("oi", page.locator(("text=oi >> nth=0")).text_content())

    def write_code(self, page):
        page.locator("text=xxxxxxxxxx 1#Start your python function here >> div[role='presentation']").click()
        page.keyboard.press("Enter")
        page.keyboard.type("def oi():")
        page.keyboard.press("Enter")
        page.keyboard.type("    return 'oi'")
        page.click('text=Executar')
        time.sleep(5)

    def write_terminal(self, page):
        page.locator("div:nth-child(3) > .CodeMirror > .CodeMirror-scroll > .CodeMirror-sizer > div > .CodeMirror-lines > div > .CodeMirror-code").click()
        page.keyboard.type("print('oi')")

    def password_reset(self, page):
        page.goto(f"{self.live_server_url}/pt-br/accounts/login/?next=/pt-br/start")
        page.click('text=Esqueceu a senha?')
        page.fill('input#id_email', 'hugofg@dcc.ufrj.br')
        page.click("text=Enviar")
        self.assertEqual("Enviamos por e-mail instruções para redefinir sua senha, se existir uma conta com o e-mail que você digitou. Você deve recebê-las em breve.", page.locator('text=Enviamos por e-mail instruções para redefinir sua senha, se existir uma conta com o e-mail que você digitou. Você deve recebê-las em breve.').text_content().strip())

    def class_dashboard(self, page):  
        page.goto(f"{self.live_server_url}/pt-br/classes/dashboard/2")
        self.assertEqual("Progresso da turma", page.locator('text=Progresso da turma').text_content())

    def logout(self, page):
        page.get_by_text("Olá, Usuário Teste").hover()
        page.click("text=Sair")
        self.assertEqual("Welcome to  Machine Teaching", page.locator('text=Welcome to  Machine Teaching').text_content())

    def create_class(self, page):
        page.goto(f"{self.live_server_url}/pt-br/classes")
        page.fill('form[action="/pt-br/classes"] input[name="name"]', 'Turma_Teste')
        page.click("text=Criar")
        time.sleep(1)
        page.goto(f"{self.live_server_url}/pt-br/classes")
        self.assertEqual("Turma_Teste", page.locator('text=Turma_Teste').text_content())
        return page.locator('.class_code').text_content()

    def create_chapter(self, page):
        page.goto(f"{self.live_server_url}/pt-br/chapters")
        page.fill('form[action="/pt-br/new_chapter"] input[name="label"]', 'Aula_Teste')
        page.fill('form[action="/pt-br/new_chapter"] input[type="date"]', '2024-12-12')
        page.click('form[action="/pt-br/new_chapter"] button[type="submit"]') 
        page.click("text=+ Adicionar problema")

        page.keyboard.press("Enter")
        page.keyboard.press("Enter")        
        page.keyboard.press("Enter")        
        page.keyboard.press("Enter")        

        solution = """def Header_Teste(num):
                return num"""
        
        page.keyboard.type(solution)
        page.fill('form[action="/pt-br/new"] input[name="title"]', 'Exercicio_Teste')
        page.fill('form[action="/pt-br/new"] input[name="header"]', 'Header_Teste')
        page.fill('form[action="/pt-br/new"] input[name="order"]', '1')
        page.click("text=Adicionar problema")


    def test_user(self):
        page = self.browser.new_page()
        page.set_default_timeout(10000)

        #print("      - Testando sobre...")
        #self.about(page)

        print("      - Testando mudança de linguagem...")
        self.change_language(page)

        print("      - Testando termos de uso...")
        self.read_terms(page)

        print("      - Testando termos de privacidade...")
        self.read_privacy(page)


      #  print("      - Testando criação de turma...")
      #  class_code = self.create_class(page)

        OnlineClass.objects.create(name='turma', start_date='2024-01-01')
        default_class = OnlineClass.objects.get(name='turma').class_code

        print("      - Testando criação de professor e aula...")
        self.register(page, default_class, settings.TEST_GNAME, settings.TEST_SNAME, settings.TEST_MANAGER, settings.TEST_PASSWORD)
        self.create_professor(page)
        self.login(page, settings.TEST_MANAGER, settings.TEST_PASSWORD)
        class_code = self.create_class(page)
        self.create_chapter(page)
        self.logout(page)


        print("      - Testando criação de aluno...")
        self.register(page, class_code, settings.TEST_GNAME, settings.TEST_SNAME, settings.TEST_USER, settings.TEST_PASSWORD)

        print("      - Testando login...")
        self.login(page, settings.TEST_USER, settings.TEST_PASSWORD)

        print("      - Testando resolução de exercício específico...")
        self.exercise(page)

        print("      - Testando entrada do dashboard...")
        self.outcomes(page)

        print("      - Testando vista de capítulos antigos...")
        self.past_chapters( page)

        print("      - Testando vista de todos os capítulos...")
        self.chapters(page)

        print("      - Testando vista de capítulo específico...")
        self.specific_chapter(page)

        print("      - Testando vista de exercício específico...")
        self.specific_problem(page)
        self.specific_problem_2(page)

        print("      - Testando vista de próximo exercício...")
        self.next(page)

        print("      - Testando vista de soluções passadas...")
        self.past_solutions(page)
 
        print("      - Testando troca de senha...")
        self.password_reset(page)

        self.login(page, settings.TEST_MANAGER, settings.TEST_PASSWORD)
        self.class_dashboard(page)

        page.close()

# class BackendTests(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.credentials = {
#             'username': settings.TEST_SUPERUSER_EMAIL,
#             'password': settings.TEST_SUPERUSER_PASSWORD,
#             'email': settings.TEST_SUPERUSER_EMAIL,

#         }
#         User.objects.create_superuser(**self.credentials)


#     # def test_register(self):
#         new_user_data = {'username': "teste", 'password': "teste123", 'email': "teste@gmail.com"}
#         User.objects.create_user(**new_user_data)

#         find_user = User.objects.get(username="teste")
#         self.assertEqual(find_user.username, "teste")

#     # def test_create_class(self):
#         new_class_data = {'name': "teste", 'class_code': "teste123", 'start_date': "2020-01-01"}
#         OnlineClass.objects.create(**new_class_data)

#         find_class = OnlineClass.objects.get(name="teste")
#         self.assertEqual(find_class.name, "teste")

#     # def test_create_chapter(self):
#         chapter = Chapter.objects.create(
#             id=1,
#             label="Teste"
#         )   
#         self.assertEqual(chapter.label, "Teste")

#     # test_finding_chapter
#         find_chapter = Chapter.objects.get(id=1)
#         self.assertEqual(find_chapter.label, "Teste")
  
#         problem = Problem.objects.create(
#             id=1,
#             title="Teste"
#         )
#         self.assertEqual(problem.title, "Teste")

#     # test_finding_problem(self):
#         find_problem = Problem.objects.get(id=1)
#         self.assertEqual(find_problem.title, 'Teste')

#         ExerciseSet(chapter=find_chapter, problem=find_problem, order=1).save()

#     # test_chapter_problems
#         chapter = Chapter.objects.get(id=1)
#         problems = Problem.objects.filter(chapter=chapter)
#         self.assertEqual(problems.count(), 1)
#         self.assertEqual(problems[0].title, "Teste")
        
#     ## I NEED TO FIND HOW TO USER ANSWER A PROBLEM