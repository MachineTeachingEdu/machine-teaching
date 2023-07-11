function runhiddentests(hidden_args, func, expected_hidden_results){

    var correct_results = []

    var prog = editor.getValue();
    console.log('prog = ' + prog)

    // const hidden_args = ['[2]', '[5]', '[7]', '[9.5]', '[10]'];
    // const expected_hidden_results = ['2', '5', '7', '9.5', '10'];

    var mypre = document.getElementById("hidden-output");
    mypre.innerHTML = '';
    let results = [];
    Sk.pre = "hidden-output";
    Sk.configure({output: outf, read:builtinRead, __future__: Sk.python3, execLimit: 500});
    (Sk.TurtleGraphics || (Sk.TurtleGraphics = {})).target = 'mycanvas';

    for (i = 0; i < hidden_args.length; i++) {
        item = hidden_args[i];
        prog_args = prog.replaceAll('\t','    ') +
        "\nif type(" + func + "(*" + item + ")) == str:\n    print(\"'\"+" + 
        func + "(*" + item + ")+\"'\")\nelse:\n    print(" + 
        func + "(*" + item + "))";
        console.log(prog_args);
        var myPromise = Sk.misceval.asyncToPromise(function() {
            return Sk.importMainWithBody("<stdin>", false, prog_args, true);
        });
        myPromise.then(function(mod) {
            results.push('success');
            console.log('success');
        },
            function(err) {
            results.push(err.toString() + '\n');
            console.log(err.toString());
        });
    };

    setTimeout(function(){
   var final_results = [];
   var correct_items = 0;
   console.log(results);
   console.log(results.length);
   console.log(correct_results);
   for (i = 0; i < hidden_args.length; i++) {
           console.log(results[0])
       if (results[i] == 'success') {
           final_results.push(correct_results[correct_items]);
           correct_items++;
       } else {
           final_results.push(results[i]);
       }
   }
   console.log(final_results);
    correct_results = []
    mypre.innerHTML = final_results.join('');

    seconds_end_page = performance.now()
    seconds_in_page = Math.round((seconds_end_page - seconds_begin_page)/1000);

    seconds_end_code = performance.now();
    console.log("seconds in this snippet:" + Math.round(
        (seconds_end_code - seconds_begin_code)/1000));
    seconds_in_code += Math.round((seconds_end_code - seconds_begin_code)/1000);
    console.log("seconds in code: " + seconds_in_code);
    console.log("seconds in page:" + seconds_in_page);

    hidden_answers = document.getElementById("hidden-output").innerHTML.split("\n");
    errors = 0;

    hidden_eval_div = document.getElementById("hidden_eval");

    for (i = 0; i < expected_hidden_results.length; i++){
        try {
            hidden_answers_parsed = JSON.parse(hidden_answers[i].replace(/'/g, '"'));
        }
        catch(e) {
            hidden_answers_parsed = hidden_answers[i];
        }
        try {
            expected_hidden_results_parsed = JSON.parse(expected_hidden_results[i].replace(/'/g, '"'));
        } catch(e) {
            expected_hidden_results_parsed = expected_hidden_results[i];
        }
        console.log(expected_hidden_results_parsed);
        hidden_eval_div.innerHTML += `<div class="card test-case">
                            <h3>${i+1}</h3>
                            <div id="hidden-outcome-${i+1}"></div>
                            <table>
                                <tr>
                                <td class="col-4">${input}</td>
                                <td class="col-8">${func}(<span class="args">${hidden_args[i].slice(1,-1)}</span>)</td>
                                </tr>
                                <tr>
                                <td class="col-4">${expected_output}</td>
                                <td class="col-8">${expected_hidden_results[i]}</td>
                                </tr>
                                <tr>
                                <td class="col-4">${your_output}</td>
                                <td class="col-8">${hidden_answers[i]}</td>
                                </tr>
                            </table>
                            </div>`;
        var outcome = document.getElementById(`hidden-outcome-${i+1}`);
        try {
            if (JSON.stringify(expected_hidden_results_parsed, Object.keys(expected_hidden_results_parsed).sort()) == JSON.stringify(hidden_answers_parsed, Object.keys(hidden_answers_parsed).sort())){
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

    var hits = Math.round(100-100*errors/expected_hidden_results.length);
    document.getElementById('hidden-test-bar').style.cssText = `width: ${hits}%; background: var(--green);`;
    var hiddenTestSpan = document.getElementById('hidden-test-span');
    hiddenTestSpan.textContent = `${hits}%`;
    hiddenTestSpan.style.cssText = `font-size: 25px; margin-right: 1rem;`;
    if(hits !== 0){
        hiddenTestSpan.style.cssText = 'color: var(--green); font-size: 25px; margin-right: 1rem;';
    }
    $('.result').css('display','flex');
    $('#outcome').html(`
        <div ">${Math.round(expected_hidden_results.length-errors)}</div>
        <div class="task-progress2">
            <div class="passed" style="width:${hits}%"></div>
        </div>
        <div id="errors">
        ${Math.round(errors)}
        </div>`);

        document.getElementById('evaluation').style.cssText = 'display: none;';
        document.getElementById('hidden_eval').style.cssText = 'display: none;';

    }, 2000);

    function outf(text) {
        correct_results.push(text);
    }
    function builtinRead(x) {
        if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined)
                throw "File not found: '" + x + "'";
        return Sk.builtinFiles["files"][x];
}
}


const showHiddenTestCase = () => {
    const evaluation = document.getElementById('hidden_eval');
    if(evaluation.style.cssText === 'display: none;'){
        evaluation.style.cssText = 'display: flex; flex-direction: column;';
    } else {
        evaluation.style.cssText = 'display: none;';
    }
}
