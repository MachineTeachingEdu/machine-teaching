var currentLanguage = "Python";
$('#dropdown-lang').on('change', function() {
    var language = $('#dropdown-lang option:selected').text();
    dictSolutions[currentLanguage].tip = editor.getValue();
    editor.setValue(dictSolutions[language].tip);
    currentLanguage = language;
    if(language == "Python"){
        $("#python_tutor").show();
        editor.setOption('mode', {name: "python", version: 2, singleLineStringErrors: false});
        $("#interactive").parent().show();
    }
    else{
        if(language == "Julia"){
            editor.setOption('mode', { name: "julia" });
            $("#python_tutor").hide();
        }
        else if(language == "C"){
            editor.setOption('mode', { name: "text/x-csrc" });
            $("#python_tutor").show();
        }
        $("#interactive").parent().hide();    //Não teremos editor interativo se não for Python
    }
});

// output functions are configurable. This one just appends some text to a pre element.
correct_results = [];
function outf(text) {
    correct_results.push(text);
/*    var mypre = document.getElementById("output");
    mypre.innerHTML = mypre.innerHTML + text;*/
}
function builtinRead(x) {
    if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined)
            throw "File not found: '" + x + "'";
    return Sk.builtinFiles["files"][x];
}

function passed() {
  $('#next').attr('class', 'primary');
  $('#next').attr('onclick', 'gotoproblem()');
  $('#errors').css('color', '#CCCCCC');
}


function evaluateResult(args, func, expected_result, final_result, isCorrect, index, errorAJAX=false){
    let eval_div = document.getElementById("evaluation");
    let numTestCases = $(eval_div).children(".test-case").length;
    
    let newTestCase = $('<div>', { class: 'card test-case', passed: isCorrect, num: index });
    let h3 = $('<h3>').text(numTestCases+1);    //Por ser síncrono, as questões ficariam em ordem "aleatória" se eu fizer uma chamada ajax por caso de teste
    $(newTestCase).append(h3);
    let divOutcome = $('<div>', { id: 'outcome-' + (index + 1) });
    $(newTestCase).append(divOutcome);
    let table = $('<table>');
    let divOutput = document.getElementById("output");
    if(!errorAJAX){
        let row1 = $('<tr>');
        $(row1).append($('<td>', { class: 'col-4' }).text(input));
        $(row1).append($('<td>', { class: 'col-8' }).html(func + '(<span class="args">' + args.slice(1, -1) + '</span>)'));
        table.append(row1);
        var row2 = $('<tr>');
        $(row2).append($('<td>', { class: 'col-4' }).text(expected_output));
        $(row2).append($('<td>', { class: 'col-8' }).text(expected_result));
        table.append(row2);
        var row3 = $('<tr>');
        $(row3).append($('<td>', { class: 'col-4' }).text(your_output));
        $(row3).append($('<td>', { class: 'col-8' }).text(final_result));
        table.append(row3);
        if (!final_result.endsWith('\n'))
            final_result += '\n';
        divOutput.innerHTML = divOutput.innerHTML + final_result;
    }
    else{    //Se der um erro na chamada ajax
        let msgError = "Server communication error.";
        let row1 = $('<tr>');
        $(row1).append($('<td>', { class: 'col-4' }).text(msgError));
        table.append(row1);
        msgError += "\n";
        divOutput.innerHTML = divOutput.innerHTML + msgError;
    }
    newTestCase.append(table);
    $(newTestCase).css("display", "none");
    $(eval_div).append(newTestCase);
    $(newTestCase).fadeIn(500);

    //Atribuindo a insígnia de sucesso ou fracasso:
    let outcome = document.getElementById(`outcome-${index+1}`);
    if(isCorrect)
        outcome.innerHTML += `<div class="badge success">${passed_txt}</div>`
    else
        outcome.innerHTML += `<div class="badge danger">${failed_txt}</div>`
};

function postEvaluate(status_code=null, message_error=null){  //Esta função será chamada depois de todos os casos de teste terem aparecido
    //Fazendo a contagem de tempo
    seconds_end_page = performance.now()
    seconds_in_page = Math.round((seconds_end_page - seconds_begin_page)/1000);
    seconds_end_code = performance.now();
    seconds_in_code += Math.round((seconds_end_code - seconds_begin_code)/1000);
    //console.log("seconds in this snippet:" + Math.round((seconds_end_code - seconds_begin_code)/1000));
    //console.log("seconds in code: " + seconds_in_code);
    //console.log("seconds in page:" + seconds_in_page);
    //console.log("seconds to begin:" + seconds_to_begin);

    //console.log("Respostas: " + document.getElementById("output").innerHTML);
    $(".div_loading_test_cases").hide();   //Escondendo o loading na página de past_solutions

    let eval_div = document.getElementById("evaluation");
    if(message_error == null){
        let errors = $(eval_div).children('[passed=false]').length;
        let totalTestCases = $(eval_div).children('.test-case').length;

        // Display test case result
        var hits = Math.round(100-100*errors/totalTestCases);
        $('.result').css('display','flex');
        $('#outcome').html(`
            <div ">${Math.round(totalTestCases-errors)}</div>
            <div class="task-progress2">
                <div class="passed" style="width:${hits}%"></div>
            </div>
            <div id="errors">
            ${Math.round(errors)}
            </div>`);
        $('#next').remove();
        $('.result').append(`<button type="button" onclick="gotoproblem()" class="primary disabled" id="next">${next}</button>`);

        if($("#dropdown-lang").length){   //Se não estiver na página past_solutions
            language = $('#dropdown-lang option:selected').text();
            //if(totalTestCases == dictSolutions[language].test_cases.length){
            if (errors == 0) {
                passed()
                save_log('P', seconds_in_code, seconds_to_begin, seconds_in_page, hits);
            } 
            else {
                save_log('F', seconds_in_code, seconds_to_begin, seconds_in_page, hits);
            }
            //}
        }

    }
    else {   //Se o código submetido for inválido ou der erro no pré-processamento
        if(status_code == 1)   //Erro de print
            message_error = print_error;
        if(status_code == 4){   //Erro de sintaxe ou de compilação no pré-processamento
            divOutput = document.getElementById("output");
            divOutput.innerHTML = divOutput.innerHTML + message_error;
            if($("#dropdown-lang").length)
                save_log('F', seconds_in_code, seconds_to_begin, seconds_in_page, 0);
        }
        //console.log("erro de teste. status code: ", status_code, "  message_error: ", message_error);
        message_error = message_error.replace(/\n/g, "<br>");
        eval_div.innerHTML = `
        <div class="card" style="position: relative;" id="print_error">
            <div class="badge danger" style="position: absolute; top: 1rem; right: 1rem">${failed_txt}</div>
            <h3 style="margin-bottom: 0.5em">${error}</h3>
            <p style="margin-top: 0; margin-bottom: 0.1em">${message_error}</p>
        </div>`;
        $('.result').hide()
    } 
    
    $('#dropdown-lang').prop('disabled', false);
    editor.setOption('readOnly', false);
    $('#run').show();
    $('.loader').hide();
    $('.loader div').attr('style', 'width: 0;');
}

//Fazendo uma única chamada AJAX para o pré-processamento e para a execução dos testes:
function runit(lang="") {
    $('#run').hide();
    $('#dropdown-lang').prop('disabled', true);
    editor.setOption('readOnly', true);
    $('.loader').show();
    $('.loader div').animate({width: '100%'}, 8000);
    var mypre = document.getElementById("output");
    mypre.innerHTML = '';

    var code = editor.getValue();  //Get code from text editor
    let eval_div = document.getElementById("evaluation");
    eval_div.innerHTML = "";
    $('.result').css('display','none');
    let language = lang;
    if($("#dropdown-lang").length)
        language = $('#dropdown-lang option:selected').text();

    while(code.includes('\t')){
        code = code.replace('\t', '    ');
    }

    //Fazendo apenas uma requisição AJAX:
    let zip_codes = new JSZip();
    zip_codes.file("run_me", code);
    zip_codes.generateAsync({ type: "blob" }).then((content) => {
        var formData = new FormData();
        formData.append("file", content, "extract-me.zip");
        formData.append("prog_lang", language);
        formData.append("problem_id", problem_id);    //problem_id é uma variável global definida no template
        formData.append("csrfmiddlewaretoken", csrftoken);    //definida no template
        $.ajax({
            url: code_submition_url,   //definida no template
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if(response.pre_process_error){   //Se houver um erro no pré-processamento
                    let pre_process_status = response.code_status;
                    let pre_process_message = response.message;
                    $('.loader div').stop();
                    postEvaluate(pre_process_status, pre_process_message);
                    console.log("Erro no pré-processamento: ", response);
                }
                else{
                    //Se tudo for ok no pré-processamento e se for Python, será necessário usar o Skulpt para fazer o console interativo funcionar:
                    if(language == "Python"){
                        Sk.configure({});
                        var skPromise = Sk.misceval.asyncToPromise(function() {
                            return Sk.importMainWithBody("<stdin>", false, code, true);
                        });
                    }
                    let resultsNovo = {};
                    let tle = false;
                    $.each(response, function(i, response_item) {
                        let statusCode = response_item.status_code;
                        let serverName = response_item.result.hostname;
                        let output = response_item.result.code_output;
                        let prof_output = response_item.result.prof_output;
                        let isCorrect = response_item.result.isCorrect ? true : false;
                        let testCase = response_item.result.test_case;
                        let funcName = response_item.result.func_name;

                        if(statusCode == 200){
                            //console.log("Success: ", response[i]);
                            resultsNovo[i] = output;
                        }
                        else{
                            //console.log("Erro: ", response[i]);
                            var resultTxt = output;
                            resultsNovo[i] = resultTxt + '\n';
                        }
                        if (!isCorrect) {
                            if (output.toUpperCase().includes("TIME LIMIT EXCEEDED")) {   //Se der TLE em um dos casos de teste, apenas um é retornado
                                tle = true;
                                postEvaluate(99, "Time limit exceeded: O código excedeu o tempo limite de execução.");
                            }
                        }
                        evaluateResult(testCase, funcName, prof_output, resultsNovo[i], isCorrect, i);
                        //Se um dos casos de teste der um erro no servidor: ainda não definido como proceder
                    });
                    $('.loader div').stop();
                    if (!tle)
                        postEvaluate(status_code=0);
                }
            },
            error: function(error) {
                $('.loader div').stop();
                postEvaluate(-1, "Server communication error.");
                console.log("erro na chamada do ajax: ", error, "\nNão foi possível realizar o processamento do código.");
            },
        });
    });
};



function skipit() {
   // Evaluate results
   seconds_end_page = performance.now()
   seconds_in_page = Math.round((seconds_end_page - seconds_begin_page)/1000);
   console.log("seconds in page:" + seconds_in_page);
   console.log("seconds to begin: " + seconds_to_begin);
   console.log("seconds in code:" + seconds_in_code);

   save_log('S', seconds_in_code, seconds_to_begin, seconds_in_page);

   gotoproblem();
};

function gotoproblem() {
    /*location.reload();*/
    window.location.href = START;
}

function betterTab(cm) {
    if (cm.somethingSelected()) {
        cm.indentSelection("add");
    } else {
        cm.replaceSelection(cm.getOption("indentWithTabs")? "\t":
                Array(cm.getOption("indentUnit") + 1).join(" "), "end", "+input");
    }
}

// Calculating time in page and code
// Get when user stops typing
var delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

// Variables to count time
var seconds_begin_page = performance.now();
var seconds_in_code = 0;
var seconds_to_begin = 0;
var seconds_in_page = 0;
var seconds_begin_code = 0;
var first_keydown= true;
