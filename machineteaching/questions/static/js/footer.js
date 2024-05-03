function showBox() {
	$('body').append('<div class="bg2"></div>');
	$('.bg2').append('<div class="card"></div>');
	$('.bg2 .card').append(`<h3></h3>
		<span>
		  <a class="link" onclick="hideBox()">${close}</a>
		</span>
		<div class="popup-content"></div>`);
};

function hideBox() {
	$('.bg2').remove();
}

function showConditions(language) {
	if (language == "en") {
    	var title = "Terms and conditions"
    	var content = `Last updated: August 29, 2020
                <br><br>
                <h4>PRIVACY</h4>
                <ul>
                    <li>
                        We have established a Privacy Policy, which is considered
                        part of our Terms of Service. Please read the Privacy Policy to
                        understand our commitment to the privacy of our users.  
                    </li>
                    <li>
                        By registering, the user agrees that all the data
                        provided to the website may be used as anonymous data research
                        intended to enhance the Machine Teaching Platform as well as the
                        quality of learning and related sciences worldwide.
                    </li>
                </ul>
                <h4>YOUR ACCOUNT</h4>
                <ul>
                    <li>
                        When and if you register with the Site, you agree to (a) provide
                        accurate, current and complete information about yourself as
                        prompted by our registration form (including your email address),
                        (b) allow the Machine Teaching Platform to conduct A/B testing
                        using information gathered from the actions that you take with your
                        account, and maintain and update your information (including
                        your email address) to keep it accurate, current and complete. You
                        acknowledge that, if any information provided by you is untrue,
                        inaccurate, not current or incomplete, we reserve the right to
                        terminate this Agreement and your access to the Site. As part of
                        the registration process, you will be asked to select a username
                        and password. We may refuse to grant you a username that
                        impersonates someone else, is or may be illegal, is or may be
                        protected by trademark or other proprietary rights law, is vulgar
                        or otherwise offensive, or may cause confusion, as determined by us
                        in our sole discretion. You will be responsible for the
                        confidentiality and use of your username and password and agree not
                        to transfer or resell your use of or access to the Site to any
                        third party. If you have reason to believe that your account with
                        us is no longer secure, you must promptly change your password. YOU
                        ARE ENTIRELY RESPONSIBLE FOR MAINTAINING THE CONFIDENTIALITY OF
                        YOUR USERNAME AND PASSWORD AND FOR ANY AND ALL ACTIVITIES THAT ARE
                        CONDUCTED THROUGH YOUR ACCOUNT.  
                    </li>
                </ul>
                <h4>DISCLAIMERS</h4>
                <ul>
                    <li>
                       The Machine Teaching developers have worked hard to develop services
                       and materials on this Site that assist students, educators, parents,
                       and guardians in the
                       learning process. Nonetheless, THE SITE, THE MATERIALS ON THE SITE,
                       AND ANY PRODUCT OR SERVICE OBTAINED THROUGH THE SITE ARE PROVIDED
                       "AS IS" AND WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
                       IMPLIED, INCLUDING, WITHOUT LIMITATION, IMPLIED WARRANTIES OF TITLE,
                       NON-INFRINGEMENT, ACCURACY, MERCHANTABILITY, AND FITNESS FOR A
                       PARTICULAR PURPOSE, AND ANY WARRANTIES THAT MAY ARISE FROM COURSE OF
                       DEALING, COURSE OF PERFORMANCE OR USAGE OF TRADE. Specifically and
                       without limitation, THE PLATFORM AND ITS AFFILIATES, LICENSORS, SUPPLIERS,
                       SPONSORS AND AGENTS DO NOT WARRANT THE SERVICES ON THIS SITE WILL BE
                       UNINTERRUPTED, SECURE, OR ERROR-FREE; THAT THE SITE IS FREE OF
                       VIRUSES OR OTHER HARMFUL COMPONENTS; THAT THE CONTENT ON THE SITE IS
                       ENTIRELY CORRECT, ACCURATE, UP-TO-DATE, OR RELIABLE; THAT DEFECTS
                       WILL BE CORRECTED, OR THAT THE SITE, THE SERVER(S) ON WHICH THE SITE
                       IS HOSTED OR SOFTWARE ARE FREE OF VIRUSES OR OTHER HARMFUL
                       COMPONENTS. ANY MATERIAL DOWNLOADED OR OTHERWISE OBTAINED THROUGH
                       THE USE OF THE SERVICE IS DONE AT YOUR OWN DISCRETION AND RISK AND
                       THAT YOU WILL BE SOLELY RESPONSIBLE FOR ANY DAMAGE TO YOUR COMPUTER
                       SYSTEM OR LOSS OF DATA THAT RESULTS FROM THE DOWNLOAD OF ANY SUCH
                       MATERIAL. YOUR USE OF THE SITE AND ANY MATERIALS PROVIDED THROUGH
                       THE SITE IS ENTIRELY AT YOUR OWN RISK.
                    </li>
                </ul>
                <h4>CONTACT INFORMATION</h4>
                <ul>
                    <li>
                       If you have any questions or concerns about this 
                       Terms and Conditions,
                       please contact us at:
                       laura.moraes@coppe.ufrj.br.
                    </li>
                </ul>`}
    else {
    	var title = "Termos e condições"
    	var content = `Última atualização: 29 de Agosto de 2020
                <br><br>
                <h4>PRIVACIDADE</h4>
                <ul>
                    <li>
                        Estabelecemos uma Política de Privacidade, que é considerada parte de
                        nossos Termos de Serviço. Leia a Política de Privacidade para entender
                        nosso compromisso com a privacidade de nossos usuários.
                    </li>
                    <li>
                        Ao se cadastrar, o usuário concorda que todos os dados fornecidos ao site
                        podem ser usados nesta pesquisa como dados anônimos com o objetivo de 
                        aprimorar a Plataforma Machine Teaching, bem como a qualidade do aprendizado
                        e ciências afins em todo o mundo.
                    </li>
                </ul>
                <h4>SUA CONTA</h4>
                <ul>
                    <li>
                        When and if you register with the Site, you agree to (a) provide
                        accurate, current and complete information about yourself as
                        prompted by our registration form (including your email address),
                        (b) allow the Machine Teaching Platform to conduct A/B testing
                        using information gathered from the actions that you take with your
                        account, and maintain and update your information (including
                        your email address) to keep it accurate, current and complete. You
                        acknowledge that, if any information provided by you is untrue,
                        inaccurate, not current or incomplete, we reserve the right to
                        terminate this Agreement and your access to the Site. As part of
                        the registration process, you will be asked to select a username
                        and password. We may refuse to grant you a username that
                        impersonates someone else, is or may be illegal, is or may be
                        protected by trademark or other proprietary rights law, is vulgar
                        or otherwise offensive, or may cause confusion, as determined by us
                        in our sole discretion. You will be responsible for the
                        confidentiality and use of your username and password and agree not
                        to transfer or resell your use of or access to the Site to any
                        third party. If you have reason to believe that your account with
                        us is no longer secure, you must promptly change your password. YOU
                        ARE ENTIRELY RESPONSIBLE FOR MAINTAINING THE CONFIDENTIALITY OF
                        YOUR USERNAME AND PASSWORD AND FOR ANY AND ALL ACTIVITIES THAT ARE
                        CONDUCTED THROUGH YOUR ACCOUNT.  
                    </li>
                </ul>
                <h4>TERMO DE RESPONSABILIDADE</h4>
                <ul>
                    <li>
                       The Machine Teaching developers have worked hard to develop services
                       and materials on this Site that assist students, educators, parents,
                       and guardians in the
                       learning process. Nonetheless, THE SITE, THE MATERIALS ON THE SITE,
                       AND ANY PRODUCT OR SERVICE OBTAINED THROUGH THE SITE ARE PROVIDED
                       "AS IS" AND WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
                       IMPLIED, INCLUDING, WITHOUT LIMITATION, IMPLIED WARRANTIES OF TITLE,
                       NON-INFRINGEMENT, ACCURACY, MERCHANTABILITY, AND FITNESS FOR A
                       PARTICULAR PURPOSE, AND ANY WARRANTIES THAT MAY ARISE FROM COURSE OF
                       DEALING, COURSE OF PERFORMANCE OR USAGE OF TRADE. Specifically and
                       without limitation, THE PLATFORM AND ITS AFFILIATES, LICENSORS, SUPPLIERS,
                       SPONSORS AND AGENTS DO NOT WARRANT THE SERVICES ON THIS SITE WILL BE
                       UNINTERRUPTED, SECURE, OR ERROR-FREE; THAT THE SITE IS FREE OF
                       VIRUSES OR OTHER HARMFUL COMPONENTS; THAT THE CONTENT ON THE SITE IS
                       ENTIRELY CORRECT, ACCURATE, UP-TO-DATE, OR RELIABLE; THAT DEFECTS
                       WILL BE CORRECTED, OR THAT THE SITE, THE SERVER(S) ON WHICH THE SITE
                       IS HOSTED OR SOFTWARE ARE FREE OF VIRUSES OR OTHER HARMFUL
                       COMPONENTS. ANY MATERIAL DOWNLOADED OR OTHERWISE OBTAINED THROUGH
                       THE USE OF THE SERVICE IS DONE AT YOUR OWN DISCRETION AND RISK AND
                       THAT YOU WILL BE SOLELY RESPONSIBLE FOR ANY DAMAGE TO YOUR COMPUTER
                       SYSTEM OR LOSS OF DATA THAT RESULTS FROM THE DOWNLOAD OF ANY SUCH
                       MATERIAL. YOUR USE OF THE SITE AND ANY MATERIALS PROVIDED THROUGH
                       THE SITE IS ENTIRELY AT YOUR OWN RISK.
                    </li>
                 </ul>
                <h4>CONTATO</h4>
                <ul>
                    <li>
                       Se você ainda possui alguma dúvida ou preocupações sobre este
                       Termos e Condições,
                       contate-nos em:
                       laura.moraes@coppe.ufrj.br.
                    </li>
                </ul>`}

	showBox()
	$('.bg2 .card h3').append(title);
	$('.bg2 .card div').append(content);
};

function showPrivacy(language) {
	if (language == "en") {
    	var title = "Privacy policy"
    	var content = `Last updated: August 29, 2020
            <br><br>
            <h4>COMMERCIAL USE </h4>
            <ul>
                <li>
                   
                   Machine Teaching will never use our Platform for commercial use. We
                   will never advertise on our site.  Additionally, we will never sell
                   personally identifiable or non-personally identifiable information
                   to third parties.  
                   
                </li>
                <li>
                   
                    If you wish to become a Registered User (Student User or Teacher
                    User) of the Platform, you must provide us with certain information
                    as part of the registration process. In this Privacy Policy, when
                    we use the term "Personally Identifiable Information", we mean any
                    information that can be used to identify or contact a specific
                    individual. We use Personally Identifiable Information to process
                    requests made through this Site and Platform, such as registration
                    requests. The user name that is assigned to you during the
                    registration process will identify you on the Platform in
                    conjunction with content that you submit to the Platform, and this
                    information may be viewed by Users. All passwords are salted before
                    being stored, so we are not aware of the passwords of any users.
                   
                </li>
                <li>
                    
                   Personally Identifiable Information and other data that you
                   furnished through the Platform may remain in our records even if you
                   are no longer a User and can be used by us in accordance with this
                   Privacy Policy.  
                   
                </li>
                <li>
                    
                   We may collect certain information automatically when you visit the
                   Platform or Site, such as the browser you are using, the Internet
                   address from which you linked to the Platform or Site, the operating
                   system of your computer, the unique IP address of the computer you
                   used to access the Platform or Site and usage and browsing habits.
                   We use this information to administer and improve your experience on
                   the Platform and Site, to help diagnose and troubleshoot potential
                   server malfunctions, and to gather broad demographic information. If
                   a Student User enters a class code provided by a Teacher User, then
                   the Teacher User may view information about that student.  
                   
                </li>
                <li>
                    
                    To help make sure you receive information that is relevant to you,
                    the Platform uses data "cookies." These cookies are small data
                    files stored on your computer that identify you as a previous
                    visitor to the Platform and help us to personalize your experience
                    when you arrive. Most web browsers are set to accept cookies. You
                    can instruct your browser not to accept cookies. However, if you
                    disable this function, you will not be able to use some of the
                    features on the Platform.
                   
                </li>
                <li>
                    
                   We work with third parties who provide services such as data
                   analysis (for example we may use Google Analytics), infrastructure
                   provision (for example we use Microsoft Azure), IT services (for
                   example we may use Cloudfare to prevent denial of service attacks),
                   email delivery services (for example we may use MailChimp to communicate
                   with non-student stakeholders), and other similar services. We may
                   share Personally Identifiable Information about account holders with
                   these parties solely for the purpose of enabling them to provide
                   these services. We only share with those that have privacy policies
                   entirely consistent with our privacy policy.
                   
                </li>
                <li>
                    
                   We may use Personally Identifiable Information about you for
                   internal purposes, including without limitation data analysis and
                   audits. If you are a Student User, your respective Teacher User may
                   also choose to share related information that they might find useful
                   to the research, such as exams and assignments grades taken
                   offline and outside the Platform.  
                   
                </li>
                <li>
                    
                   Notwithstanding any other provision of this Policy to the contrary,
                   we reserve the right to disclose your Personally Identifiable
                   Information to others as we believe to be appropriate (a) under
                   applicable law; (b) to comply with legal process (c) to respond to
                   governmental requests; (d) to enforce our Terms of Service; (e) to
                   protect our operations; (f) to protect the rights, privacy, safety
                   or property of you or others; and (g) to permit us to pursue
                   available remedies or limit the damages that we may sustain. For
                   example, we may, to the fullest extent the law allows, disclose
                   Personally Identifiable Information about you to law enforcement
                   agencies to assist them in identifying individuals who have been or
                   may be engaged in unlawful activities.  
                   
                </li>
            </ul>
            <h4>NON-PERSONALLY IDENTIFIABLE INFORMATION</h4>
            <ul>
                <li>
                    
                    Non-Personally Identifiable Information is aggregated information,
                    demographic information, and other information that does not reveal
                    a person’s specific identity. We may collect Non-Personally
                    Identifiable Information (e.g., interests, geographic location, zip
                    codes, etc.) when you voluntarily provide such information to us,
                    such as through survey responses. Such information constitutes
                    Non-Personally Identifiable Information because, unless combined
                    with your name or other Personally Identifiable Information, it
                    does not personally identify you or any other user. We retain
                    aggregated student data exclusively for the educational purpose of
                    improving the Machine Teaching Platform.
                   
                </li>
                <li>
                    
                    Additionally, we may aggregate Personally Identifiable Information
                    in a manner such that the end product does not personally identify
                    you or any other user of the Platform or Site. For example, we
                    might use Personally Identifiable Information to calculate the
                    percentage of our Users who have a particular zip code. Such
                    aggregate information is considered Non-Personally Identifiable
                    Information for purposes of this Policy. Because Non-Personally
                    Identifiable Information does not personally identify you, we may
                    use or disclose such information for any purpose. Upon request,
                    user names and birthdates will be removed leaving only
                    ‘non-personally identifiable information”.  Student generated
                    content, other than answers to test questions, will also be
                    destroyed.
                   
                </li>
            </ul>
            <h4>DATA SECURITY AND BREACH INCIDENT RESPONSE PLAN</h4>
            <ul>
                <li>
                    
                    We have implemented software and hardware security measures
                    intended to protect your Personally Identifiable Information from
                    unauthorized access. Although we strive to protect
                    your information, we cannot ensure or warrant the security of any
                    information you transmit to us through or in connection with the
                    Platform. Despite our precautions, no system can completely protect
                    against unauthorized access to your Personally Identifiable
                    Information, and your use of the Platform indicates that you are
                    willing to assume this risk. If you have reason to believe that
                    your interaction with us is no longer secure, you must immediately
                    notify us of the problem by contacting us.
                   
                </li>
            </ul>
            <h4>CONTACT INFORMATION</h4>
            <ul>
                <li>
                   If you have any questions or concerns about this 
                   Privacy Policy,
                   please contact us at: 
                   laura.moraes@coppe.ufrj.br.       
                </li>
            </ul>`
    }
    else {
        var title = "Política de privacidade"
        var content = `Última atualização: 29 de Agosto de 2020
            <br><br>
            <h4>COMMERCIAL USE </h4>
            <ul>
                <li>
                   
                   Machine Teaching will never use our Platform for commercial use. We
                   will never advertise on our site.  Additionally, we will never sell
                   personally identifiable or non-personally identifiable information
                   to third parties.  
                   
                </li>
                <li>
                   
                    If you wish to become a Registered User (Student User or Teacher
                    User) of the Platform, you must provide us with certain information
                    as part of the registration process. In this Privacy Policy, when
                    we use the term "Personally Identifiable Information", we mean any
                    information that can be used to identify or contact a specific
                    individual. We use Personally Identifiable Information to process
                    requests made through this Site and Platform, such as registration
                    requests. The user name that is assigned to you during the
                    registration process will identify you on the Platform in
                    conjunction with content that you submit to the Platform, and this
                    information may be viewed by Users. All passwords are salted before
                    being stored, so we are not aware of the passwords of any users.
                   
                </li>
                <li>
                    
                   Personally Identifiable Information and other data that you
                   furnished through the Platform may remain in our records even if you
                   are no longer a User and can be used by us in accordance with this
                   Privacy Policy.  
                   
                </li>
                <li>
                    
                   We may collect certain information automatically when you visit the
                   Platform or Site, such as the browser you are using, the Internet
                   address from which you linked to the Platform or Site, the operating
                   system of your computer, the unique IP address of the computer you
                   used to access the Platform or Site and usage and browsing habits.
                   We use this information to administer and improve your experience on
                   the Platform and Site, to help diagnose and troubleshoot potential
                   server malfunctions, and to gather broad demographic information. If
                   a Student User enters a class code provided by a Teacher User, then
                   the Teacher User may view information about that student.  
                   
                </li>
                <li>
                    
                    To help make sure you receive information that is relevant to you,
                    the Platform uses data "cookies." These cookies are small data
                    files stored on your computer that identify you as a previous
                    visitor to the Platform and help us to personalize your experience
                    when you arrive. Most web browsers are set to accept cookies. You
                    can instruct your browser not to accept cookies. However, if you
                    disable this function, you will not be able to use some of the
                    features on the Platform.
                   
                </li>
                <li>
                    
                   We work with third parties who provide services such as data
                   analysis (for example we may use Google Analytics), infrastructure
                   provision (for example we use Microsoft Azure), IT services (for
                   example we may use Cloudfare to prevent denial of service attacks),
                   email delivery services (for example we may use MailChimp to communicate
                   with non-student stakeholders), and other similar services. We may
                   share Personally Identifiable Information about account holders with
                   these parties solely for the purpose of enabling them to provide
                   these services. We only share with those that have privacy policies
                   entirely consistent with our privacy policy.
                   
                </li>
                <li>
                    
                   We may use Personally Identifiable Information about you for
                   internal purposes, including without limitation data analysis and
                   audits. If you are a Student User, your respective Teacher User may
                   also choose to share related information that they might find useful
                   to the research, such as exams and assignments grades taken
                   offline and outside the Platform.  
                   
                </li>
                <li>
                    
                   Notwithstanding any other provision of this Policy to the contrary,
                   we reserve the right to disclose your Personally Identifiable
                   Information to others as we believe to be appropriate (a) under
                   applicable law; (b) to comply with legal process (c) to respond to
                   governmental requests; (d) to enforce our Terms of Service; (e) to
                   protect our operations; (f) to protect the rights, privacy, safety
                   or property of you or others; and (g) to permit us to pursue
                   available remedies or limit the damages that we may sustain. For
                   example, we may, to the fullest extent the law allows, disclose
                   Personally Identifiable Information about you to law enforcement
                   agencies to assist them in identifying individuals who have been or
                   may be engaged in unlawful activities.  
                   
                </li>
            </ul>
            <h4>NON-PERSONALLY IDENTIFIABLE INFORMATION</h4>
            <ul>
                <li>
                    
                    Non-Personally Identifiable Information is aggregated information,
                    demographic information, and other information that does not reveal
                    a person’s specific identity. We may collect Non-Personally
                    Identifiable Information (e.g., interests, geographic location, zip
                    codes, etc.) when you voluntarily provide such information to us,
                    such as through survey responses. Such information constitutes
                    Non-Personally Identifiable Information because, unless combined
                    with your name or other Personally Identifiable Information, it
                    does not personally identify you or any other user. We retain
                    aggregated student data exclusively for the educational purpose of
                    improving the Machine Teaching Platform.
                   
                </li>
                <li>
                    
                    Additionally, we may aggregate Personally Identifiable Information
                    in a manner such that the end product does not personally identify
                    you or any other user of the Platform or Site. For example, we
                    might use Personally Identifiable Information to calculate the
                    percentage of our Users who have a particular zip code. Such
                    aggregate information is considered Non-Personally Identifiable
                    Information for purposes of this Policy. Because Non-Personally
                    Identifiable Information does not personally identify you, we may
                    use or disclose such information for any purpose. Upon request,
                    user names and birthdates will be removed leaving only
                    ‘non-personally identifiable information”.  Student generated
                    content, other than answers to test questions, will also be
                    destroyed.
                   
                </li>
            </ul>
            <h4>DATA SECURITY AND BREACH INCIDENT RESPONSE PLAN</h4>
            <ul>
                <li>
                    
                    We have implemented software and hardware security measures
                    intended to protect your Personally Identifiable Information from
                    unauthorized access. Although we strive to protect
                    your information, we cannot ensure or warrant the security of any
                    information you transmit to us through or in connection with the
                    Platform. Despite our precautions, no system can completely protect
                    against unauthorized access to your Personally Identifiable
                    Information, and your use of the Platform indicates that you are
                    willing to assume this risk. If you have reason to believe that
                    your interaction with us is no longer secure, you must immediately
                    notify us of the problem by contacting us.
                   
                </li>
            </ul>
            <h4>CONTACT INFORMATION</h4>
            <ul>
                <li>
                   Se você ainda possui alguma dúvida ou preocupações sobre este 
                   Política de Privacidade,
                   contate-nos em:
                   laura.moraes@coppe.ufrj.br.
                </li>
            </ul>`
    }

	showBox()
	$('.bg2 .card h3').append(title);
	$('.bg2 .card div').append(content);
};

var logos = `<div class="logos" style="display: flex; align-items: center; flex-direction: column;">
                <div class="logos-row">
                    <a href="http://ufrj.br/">
                    <img src="${ufrj}"></a>
                    <a href="http://cnpq.br/">
                    <img src="${cnpq}"></a>
                </div>
                <div class="logos-row">
                    <a href="http://faperj.br/">
                    <img src="${faperj}"></a>
                    <a href="http://dcc.ufrj.br/">
                    <img src="${dcc}"></a>
                    <a href="http://coppe.ufrj.br/">
                    <img src="${coppe}"></a>
                </div>
                <div class="logos-row">
                    <a href="http://cos.ufrj.br/">
                    <img src="${pesc}"></a>
                    <a href="https://www.reditus.org.br">
                    <img src="${reditus}"></a>
                </div>
             <br><br>
             </div>`

var universidades = `
        <div class="logos" style="display: flex; align-items: center; flex-direction: column;">
            <div class="logos-row">
                <a href="http://ufrj.br/">
                <img src="${ufrj}"></a>
                <a href="https://www.uah.es/es/">
                <img src="${unialcalá}"></a>
            </div>
        </div>
        `


function showAbout(url) {
	$('body').append('<div class="bg2"></div>');
	$('.bg2').append('<div class="card"></div>');
	$('.bg2 .card').append(`<h3></h3>
		<span>
		  <a class="link" onclick="hideBox()">${close}</a>
		</span>
		<div class="popup-content"><iframe src=` + url + ` title="Pagina About"></iframe></div>`);

	showBox()
	//$('.bg2 .card h3').append(title);
	//$('.bg2 .card div').append(content);
};


function showTutorials(language) {
  if (language == "en") {
      var title = "Tutorials"
      var content = `<div class="tutorials">
      <div style='height: 400px; margin-bottom: 60px;'><h3>Tips</h3><iframe src="${pdf}" type="application/pdf" style="height: -webkit-fill-available; width: -webkit-fill-available"></iframe></div> 
      <div><h3>How to register?</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/5GSyIPOux4I" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div><div>
      <h3>How to answer a problem?</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/T5VY5eJvAlc" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div><div><h3>Tricks to study</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/zbt71gP0EDk" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div></div>`
    }
    else {
      var title = "Tutoriais"
      var content = `<div class="tutorials">
      <div><h3>Dicas</h3>
      <iframe src="${pdf}" type="application/pdf" style='height: 315px; width: 560px;'></iframe>
      </div><div><h3>Como se cadastrar?</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/5GSyIPOux4I" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div><div><h3>Como responder um exercício?</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/T5VY5eJvAlc" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div><div><h3>Truques para estudar</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/zbt71gP0EDk" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div></div>`
    }

  showBox()
  $('.bg2 .card h3').append(title);
  $('.bg2 .card div').append(content);
};