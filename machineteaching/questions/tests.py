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
        cls.browser = cls.playwright.chromium.launch(headless=True) 
        User.objects.create_superuser(username=settings.TEST_SUPERUSER_USER, email=settings.TEST_SUPERUSER_EMAIL, password=settings.TEST_SUPERUSER_PASSWORD)
 
    @classmethod 
    def tearDownClass(cls): 
        cls.browser.close() 
        cls.playwright.stop() 
        super().tearDownClass() 
    
    ## Testes de Interface
    def about(self, page):
        page.goto(f"{self.live_server_url}/pt-br")
        page.click('.footer-right span:nth-child(3)')
        self.assertEqual('Sobre a pesquisa', page.locator('.bg2 .card h3:nth-child(1)').text_content())

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

    def create_class(self, page):
        page.goto(f"{self.live_server_url}/pt-br/admin/")
        page.fill('#id_username', settings.TEST_SUPERUSER_EMAIL)
        page.fill('#id_password', settings.TEST_SUPERUSER_PASSWORD)
        page.click('text=Acessar')
        page.goto(f"{self.live_server_url}/pt-br/admin/questions/onlineclass/add/")
        page.fill('#id_name', 'Teste')
        page.fill('#id_start_date', '01/01/2022')
        page.click('text=Salvar')
        class_code = page.locator('.field-class_code').text_content()
        return class_code

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
        self.assertEqual("início", page.locator('.content .topbar-left .title').text_content())

    ### não está sendo usada
    def next(self, page):
        page.goto(f"{self.live_server_url}/pt-br/next")
        self.assertEqual("Finalizado", page.locator('.content .topbar-left .title').text_content())
    
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
        self.assertEqual("Entrega", page.locator('text=Entrega').text_content())

    def past_solutions(self, page):
        page.goto(f"{self.live_server_url}/pt-br/problem_solutions/1")
        self.assertEqual("Problema atual", page.locator('text=Problema atual').text_content())

    def create_chapter(self, page):
        page.goto(f"{self.live_server_url}/pt-br/admin/questions/problem/add/")
        page.fill('#id_title', 'Teste')
        page.fill('#id_content', 'para testar')
        page.click('text=Salvar')
        page.goto(f"{self.live_server_url}/pt-br/admin/questions/chapter/add/")
        page.fill('#id_label', 'Teste aula')
        page.locator('#id_exerciseset_set-0-problem').select_option(value='1')
        page.fill('#id_exerciseset_set-0-order', '1')
        page.click('text=Salvar')
        page.goto(f"{self.live_server_url}/pt-br/admin/questions/solution/add/")
        page.fill('#id_content', 'def teste():\n    pass')
        page.fill('#id_header', 'Teste')
        page.click('b[role="presentation"]')
        page.click('text=1 - Teste')
        page.click('text=Salvar')

    def create_professor(self, page, class_code):
        page.goto(f"{self.live_server_url}/pt-br/admin/")
        page.fill('#id_username', settings.TEST_SUPERUSER_EMAIL)
        page.fill('#id_password', settings.TEST_SUPERUSER_PASSWORD)
        page.click('input[type="submit"]')
        page.click('text=Grupos')
        page.click('text=Adicionar grupo')
        page.fill('#id_name', 'Professor')
        page.click('text=Escolher todos')
        page.click('text=Salvar')
        page.click('text=Início')
        page.click('text=Professores')
        page.click('text=Adicionar professor')
        Professor.objects.create(user=User.objects.get(username=settings.TEST_MANAGER))
        p = Professor.objects.get(user=User.objects.get(username=settings.TEST_MANAGER))
        o = OnlineClass.objects.get(class_code=class_code)
        p.prof_class.add(o)
        p.save()

        # page.click('b[role="presentation"]')
        # page.click('text={}'.format(settings.TEST_MANAGER))
        # page.click('text=Escolher todos')
        # page.click('text=Salvar')

    def assign_exercise(self, page):
        self.login(page, settings.TEST_MANAGER, settings.TEST_PASSWORD)
        page.goto(f"{self.live_server_url}/pt-br/classes/manage/1")
        print(page.locator("html").inner_html())
        page.fill('input[type="date"]', '2022-12-12')
        page.fill('input[name="time"]', '23:59')
        page.click('text=Adicionar')     

    def exercise(self, page):
        page.goto(f"{self.live_server_url}/pt-br/1")
        self.assertEqual("Teste", page.locator('text=Teste Pular >> h3').text_content())
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

    def write_terminal(self, page):
        page.locator("div:nth-child(3) > .CodeMirror > .CodeMirror-scroll > .CodeMirror-sizer > div > .CodeMirror-lines > div > .CodeMirror-code").click()
        page.keyboard.type("print('oi')")
        

    def test_user(self):
        page = self.browser.new_page()
        page.set_default_timeout(10000)

        print("      - Testando sobre...")
        self.about(page)

        print("      - Testando mudança de linguagem...")
        self.change_language(page)

        print("      - Testando termos de uso...")
        self.read_terms(page)

        print("      - Testando termos de privacidade...")
        self.read_privacy(page)
        
        print("      - Testando criação de turma...")
        class_code = self.create_class(page)

        print("      - Testando criação de capítulo...")
        self.create_chapter(page)

        print("      - Testando criação de professor e aula...")
        self.register(page, class_code, settings.TEST_GNAME, settings.TEST_SNAME, settings.TEST_MANAGER, settings.TEST_PASSWORD)
        self.create_professor(page, class_code)
        self.assign_exercise(page)

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
 
        page.close()