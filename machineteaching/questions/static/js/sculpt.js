var currentLanguage = "Python";
$('#dropdown-lang').on('change', function() {
    var language = $('#dropdown-lang option:selected').text();
    dictSolutions[currentLanguage].text = editor.getValue();
    editor.setValue(dictSolutions[language].text);
    currentLanguage = language;
    if(language == "Python"){
        editor.setOption('mode', {name: "python", version: 2, singleLineStringErrors: false});
        $("#interactive").parent().show();
    }
    else{
        if(language == "Julia")
            editor.setOption('mode', { name: "julia" });
        else if(language == "C")
            editor.setOption('mode', { name: "text/x-csrc" });
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
    let h3 = $('<h3>').text(numTestCases+1);    //Por ser síncrono, as questões ficariam em ordem "aleatória"
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
    $(newTestCase).fadeIn();

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
/*
        if($("#dropdown-lang").length){
            if (errors == 0) {
                passed()
                save_log('P', seconds_in_code, seconds_to_begin, seconds_in_page, hits);
            } else {
                save_log('F', seconds_in_code, seconds_to_begin, seconds_in_page, hits);
            };
        }
*/
    }
    else {   //Se o código submetido for inválido ou der erro no pré-processamento
        if(status_code == 1)   //Erro de print
            message_error = print_error;
        if(status_code == 4){   //Erro de sintaxe ou de compilação
            divOutput = document.getElementById("output");
            divOutput.innerHTML = divOutput.innerHTML + message_error;
            //save_log('F', seconds_in_code, seconds_to_begin, seconds_in_page, 0);
        }
        eval_div.innerHTML = `
        <div class="card" style="position: relative;" id="print_error">
            <div class="badge danger" style="position: absolute; top: 1rem; right: 1rem">${failed_txt}</div>
            <h3>${error}</h3>
            <p>${message_error}</p>
        </div>`;
        $('.result').hide()
    } 
   
    $('#run').show();
    $('.loader').hide();
    $('.loader div').attr('style', 'width: 0;');
}


function evaluate(args, func, expected_results){
    eval_div = document.getElementById("evaluation");
    eval_div.innerHTML = "";
   // Get code
   var prog = editor.getValue();

    if (prog.includes('print(')) {
        save_log('F', seconds_in_code, seconds_to_begin, seconds_in_page, 0);
        eval_div.innerHTML = `
        <div class="card" style="position: relative;" id="print_error">
            <div class="badge danger" style="position: absolute; top: 1rem; right: 1rem">${failed_txt}</div>
            <h3>${error}</h3>
            <p>${print_error}</p>
        </div>`;
        $('.result').hide()
    } else {
    answers = document.getElementById("output").innerHTML.split("\n");
    //console.log("Respostas: " + answers);
    errors = 0;

    // For each test, compare results
    for (i = 0; i < expected_results.length; i++){
        //console.log(answers[i]);
        try {
            // Permite a correção de dicionários fora de ordem
            // answers_parsed = JSON.parse(answers[i]);
            answers_parsed = JSON.parse(answers[i].replace(/'/g, '"'));
        }
        catch(e) {
            answers_parsed = answers[i];
        }
        //console.log(answers_parsed)
        try {
            // Permite a correção de dicionários fora de ordem
            //expected_results_parsed = JSON.parse(expected_results[i]);
            expected_results_parsed = JSON.parse(expected_results[i].replace(/'/g, '"'));
        } catch(e) {
            expected_results_parsed = expected_results[i];
        }
        console.log("final_result_parsed: " + answers_parsed + "   expected_result_parsed: " + expected_results_parsed);
        eval_div.innerHTML += `<div class="card test-case">
                               <h3>${i+1}</h3>
                               <div id="outcome-${i+1}"></div>
                               <table>
                                 <tr>
                                   <td class="col-4">${input}</td>
                                   <td class="col-8">${func}(<span class="args">${args[i].slice(1,-1)}</span>)</td>
                                 </tr>
                                 <tr>
                                   <td class="col-4">${expected_output}</td>
                                   <td class="col-8">${expected_results[i]}</td>
                                 </tr>
                                 <tr>
                                   <td class="col-4">${your_output}</td>
                                   <td class="col-8">${answers[i]}</td>
                                 </tr>
                               </table>
                               </div>`;
        var outcome = document.getElementById(`outcome-${i+1}`);
        try {
            //console.log("final_result: " + JSON.stringify(answers_parsed, Object.keys(answers_parsed).sort()));
            //console.log("expected_result: " + JSON.stringify(expected_results_parsed, Object.keys(expected_results_parsed).sort()));
            if (JSON.stringify(expected_results_parsed, Object.keys(expected_results_parsed).sort()) == JSON.stringify(answers_parsed, Object.keys(answers_parsed).sort())){
            //if (JSON.stringify(expected_results[i]) == JSON.stringify(answers[i])){
                outcome.innerHTML += `<div class="badge success">${passed_txt}</div>`
            } else {
                outcome.innerHTML += `<div class="badge danger">${failed_txt}</div>`
                errors++;
            };
        } catch(e) {
            outcome.innerHTML += `<div class="badge danger">${failed_txt}</div>`
            errors++;
        }
    }

    // Display test case result
    var hits = Math.round(100-100*errors/expected_results.length);
    $('.result').css('display','flex');
    $('#outcome').html(`
        <div ">${Math.round(expected_results.length-errors)}</div>
        <div class="task-progress2">
            <div class="passed" style="width:${hits}%"></div>
        </div>
        <div id="errors">
        ${Math.round(errors)}
        </div>`);
    $('#next').remove();
    $('.result').append(`<button type="button" onclick="gotoproblem()" class="primary disabled" id="next">${next}</button>`);
    
    /*   DESCOMENTAR ISSO AQUI DEPOIS!!!!
    // If no errors are found, go to the next problem
    if (errors == 0) {
        passed()
        save_log('P', seconds_in_code, seconds_to_begin, seconds_in_page, hits);
    } else {
        save_log('F', seconds_in_code, seconds_to_begin, seconds_in_page, hits);
    };
    */

    }
    
    $('#run').show();
    $('.loader').hide();
    $('.loader div').attr('style', 'width: 0;');

};

/*
// Here's everything you need to run a python program in skulpt
// grab the code from your textarea
// get a reference to your pre element for output
// configure the output function
// call Sk.importMainWithBody()

function runit(args, func, expected_results) {
  $('#run').hide();
  $('.loader').show();
  $('.loader div').animate({width: '100%'}, 2000);
  //console.log("args: " + args);
  //console.log("func: " + func);
  //console.log("expected_results: " + expected_results);

   // Get code
   var prog = editor.getValue();
   //console.log("code: " + prog);


   // Prepare output display
   var mypre = document.getElementById("output");
   mypre.innerHTML = '';
   let results = [];

   Sk.pre = "output";
   Sk.configure({output:outf, read:builtinRead, __future__: Sk.python3, execLimit: 500});
   (Sk.TurtleGraphics || (Sk.TurtleGraphics = {})).target = 'mycanvas';

   // Extract data type from JSON 
   //console.log(args);

   for (i = 0; i < args.length; i++) {
       item = args[i];
       //console.log(item);
       //prog_args = prog + "\nprint(" + func + "(*" + JSON.stringify(item) + "))";
       while(prog.includes('\t')){
              prog = prog.replace('\t', '    ');
       }
       prog_args = prog +
       "\nif type(" + func + "(*" + item + ")) == str:\n    print(\"'\"+" + 
       func + "(*" + item + ")+\"'\")\nelse:\n    print(" + 
       func + "(*" + item + "))";
       // prog_args = prog + `
// try:
    // print(` + func + `(*` + item + `))
// except Exception as err:
    // print(repr(err))`
       //console.log("prog_args: " + prog_args);

       var myPromise = Sk.misceval.asyncToPromise(function() {
           return Sk.importMainWithBody("<stdin>", false, prog_args, true);
       });
       myPromise.then(function(mod) {
           results.push('success');
           //console.log('success');
           //console.log(document.getElementById("output").innerHTML);
      },
           function(err) {
           results.push(err.toString() + '\n');
           console.log(err.toString());
           //document.getElementById("output").innerHTML += err.toString() + '\n';
       });
   };

   // Wait for async run to finish
   setTimeout(function(){
       //Write results in console
       var final_results = [];
       var correct_items = 0;
       //console.log("results: " + results);
       //console.log(results.length);
       //console.log("correct_results: " + correct_results);
       //console.log("Resultados esperados: " + expected_results);
       for (i = 0; i < args.length; i++) {
            //console.log(results[0])
           if (results[i] == 'success') {
               final_results.push(correct_results[correct_items]);
               correct_items++;
           } else {
               final_results.push(results[i]);
           }
       }
       console.log("final_results: " + final_results);
       console.log("expected_results: " + expected_results);
       // Empty correct_results
       correct_results = []
       mypre.innerHTML = final_results.join('');

       // Evaluate results
       seconds_end_page = performance.now()
       seconds_in_page = Math.round((seconds_end_page - seconds_begin_page)/1000);

        seconds_end_code = performance.now();
        //console.log("seconds in this snippet:" + Math.round(
        //    (seconds_end_code - seconds_begin_code)/1000));
        seconds_in_code += Math.round((seconds_end_code - seconds_begin_code)/1000);
        //console.log("seconds in code: " + seconds_in_code);
       //console.log("seconds in page:" + seconds_in_page);
       evaluate(args, func, expected_results);


       //testeWorkerNode(prog);

       }, 2000);
};
*/


function runit(args, func, lang="") {
    $('#run').hide();
    $('.loader').show();
    $('.loader div').animate({width: '100%'}, 5000);
    var mypre = document.getElementById("output");
    mypre.innerHTML = '';

    var prog = editor.getValue();  //Get code from text editor
    let eval_div = document.getElementById("evaluation");
    eval_div.innerHTML = "";
    $('.result').css('display','none');
    let language = lang;
    if($("#dropdown-lang").length)
        language = $('#dropdown-lang option:selected').text();

    //Realizando o pré-processamento do código:
    let zip_pre_process = new JSZip();
    zip_pre_process.file("run_me", prog);
    zip_pre_process.generateAsync({ type: "blob" }).then((content) => {
        var formData = new FormData();
        formData.append("file", content, "extract-me.zip");
        formData.append("prog_lang", language);
        $.ajax({
            url: "http://localhost:5000/pre-process",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(response_pre_process) {
                //console.log("Resultado do pré-processamento: ", response_pre_process);
                let pre_process_status = response_pre_process.code_status;
                let pre_process_message = response_pre_process.message;
                let final_code = response_pre_process.final_code;
                let profCode = dictSolutions[language].solution;

                if (pre_process_status != 0){
                    $('.loader div').stop();
                    postEvaluate(pre_process_status, pre_process_message);
                    //console.log("Erro no pré-processamento: ", response_pre_process);
                }
                else {    //Código válido
                    let resultsNovo = {}
                    while(final_code.includes('\t')){
                        final_code = final_code.replace('\t', '    ');
                    }
                    if(language == "Python"){
                        Sk.configure({});
                        var skPromise = Sk.misceval.asyncToPromise(function() {
                            return Sk.importMainWithBody("<stdin>", false, final_code, true);
                        });
                    }
                    while(profCode.includes('\t')){
                        profCode = profCode.replace('\t', '    ');
                    }
                    
                    let returnType = dictSolutions[language].return_type == null ? "" : dictSolutions[language].return_type;
                    //Fazendo as requisições AJAX para cada caso de teste:
                    let zip = new JSZip();
                    zip.file("run_me", final_code);
                    zip.file("run_me_prof", profCode);   //Adicionando o arquivo com o código do professor
                    zip.generateAsync({ type: "blob" }).then((content) => {
                        let ajaxPromises = [];
                        for (let i = 0; i < args.length; i++) {
                            //if(i==0){   //para debug
                                let argList = []
                                argList.push(args[i])
                                var formData = new FormData();
                                formData.append("file", content, "extract-me.zip");   //Adicionando um campo 'file' no formData para adicionar o arquivo como um .zip
                                formData.append("args", JSON.stringify(argList));
                                formData.append("prog_lang", language);
                                formData.append("funcName", func);
                                formData.append("returnType", returnType);
                                ajaxPromises.push($.ajax({
                                    url: "http://localhost:5000/",
                                    type: "POST",
                                    data: formData,
                                    processData: false, // Necessário para enviar o FormData sem que jQuery tente processá-lo
                                    contentType: false, // Necessário para evitar que jQuery defina o Content-Type
                                    success: function(response) {
                                        let statusCode = response[0][1];
                                        let serverName = response[0][0].hostname;
                                        let output = response[0][0].code_output;
                                        let prof_output = response[0][0].prof_output;
                                        let isCorrect = response[0][0].isCorrect ? true : false;
                                        //console.log('statuscode: ', statusCode, '  servername: ', serverName, '  output: ', output);
                                        if(statusCode == 200){
                                            console.log("Success: ", response);
                                            resultsNovo[i] = output;
                                        }
                                        else{
                                            console.log("Erro: ", response);
                                            var resultTxt = output;
                                            resultsNovo[i] = resultTxt + '\n';
                                        }
                                        evaluateResult(args[i], func, prof_output, resultsNovo[i], isCorrect, i);
                                    },
                                    error: function(error) {
                                        console.log("erro na chamada do ajax: ", error);
                                        evaluateResult(null, null, null, null, false, i, true);    //Fazendo um card para os casos de erro na chamada ajax
                                    },
                                }));
                            //}
                        }
                        Promise.allSettled(ajaxPromises)    //Aqui só vai rodar quando todas as chamadas ajax terminarem ou se alguma delas der erro
                            .then(function(results) {
                                //console.log("Resultados das chamadas Ajax: ", results);
                                let errorRequests = 0;
                                for(let i=0; i<results.length; i++){
                                    if(results[i].status == "rejected")
                                        errorRequests++;
                                }
                                $('.loader div').stop();
                                postEvaluate(pre_process_status);
                            });
                    });
                    
                }
            },
            error: function(error) {
                $('.loader div').stop();
                postEvaluate(-1, "Server communication error.");
                console.log("erro na chamada do ajax: ", error, "\nNão foi possível realizar o pré-processamento do código.");
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
