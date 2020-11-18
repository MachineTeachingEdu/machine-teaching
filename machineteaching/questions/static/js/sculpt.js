// output functions are configurable.  This one just appends some text
// to a pre element.

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

function correct() {
    document.getElementById("next").style.display = "inline";
    document.getElementById("skip").style.display = "none";
    document.getElementById("next").onclick = gotoproblem;
}

function evaluate(args, expected_results){
    eval_table = document.getElementById("evaluation");
    eval_table.innerHTML = "";
    answers = document.getElementById("output").innerHTML.split("\n");
    errors = 0;

    // For each test, compare results
    for (i = 0; i < expected_results.length; i++){
        //console.log(answers[i]);
        try {
            answers_parsed = JSON.parse(answers[i].replace(/'/g, '"'));
        }
        catch(e) {
            answers_parsed = answers[i];
        }
        //console.log(answers_parsed)
        try {
            expected_results_parsed = JSON.parse(expected_results[i].replace(/'/g, '"'));
        } catch(e) {
            expected_results_parsed = expected_results[i];
        }
        //console.log(expected_results_parsed);
        eval_table.innerHTML += "<tr><td>Input:</td><td>" + args[i] + "</td></tr><tr><td>Expected output:</td><td>" + expected_results[i] + "</td></tr><tr><td>Your output:</td><td>" + answers[i] + "</td></tr>";
        try {
            if (JSON.stringify(expected_results_parsed, Object.keys(expected_results_parsed).sort()) == JSON.stringify(answers_parsed, Object.keys(answers_parsed).sort())){
            //if (JSON.stringify(expected_results[i]) == JSON.stringify(answers[i])){
                eval_table.innerHTML += '<tr><td></td><td><span class="sucess">OK</span></td></tr>'
            } else {
                eval_table.innerHTML += '<tr><td></td><td><span class="danger">OOPS!</span></td></tr>'
                errors++;
            };
        } catch(e) {
            eval_table.innerHTML += '<tr><td></td><td><span class="danger">OOPS!</span></td></tr>'
            errors++;
        }
    }

    // If no errors are found, go to the next problem
    if (errors == 0) {
        correct()
        document.getElementById("result").innerHTML = '<span class="correct" style="margin-bottom: 30px; margin-left: auto; margin-right: auto">✓</span>';
        save_log('P', seconds_in_code, seconds_to_begin, seconds_in_page);
    } else {
        document.getElementById("result").innerHTML = '<div class="wrong" style="margin-bottom: 30px; margin-left: auto; margin-right: auto">X</div>';
        save_log('F', seconds_in_code, seconds_to_begin, seconds_in_page);
    };

    //Display buttons and hide loader
    document.getElementById("buttons").style.display="block";
    document.getElementById("running").style.display="none";

    // Display result divs
    document.getElementById("output-div").style.display="block";
    document.getElementById("testcase-div").style.display="block";
}
// Here's everything you need to run a python program in skulpt
// grab the code from your textarea
// get a reference to your pre element for output
// configure the output function
// call Sk.importMainWithBody()
function runit(args, func, expected_results) {

   //Hide buttons and display loader
   document.getElementById("buttons").style.display="none";
   document.getElementById("running").style.display="block";

   // Get code
   var prog = editor.getValue();

   // Prepare output display
   var mypre = document.getElementById("output");
   mypre.innerHTML = '';
   let results = [];
   Sk.pre = "output";
   Sk.configure({output:outf, read:builtinRead, __future__: Sk.python3, execLimit: 300});
   (Sk.TurtleGraphics || (Sk.TurtleGraphics = {})).target = 'mycanvas';

   // Extract data type from JSON 
   console.log(args);

   for (i = 0; i < args.length; i++) {
       item = args[i];
       //console.log(item);
       //prog_args = prog + "\nprint(" + func + "(*" + JSON.stringify(item) + "))";
       prog_args = prog + "\nprint(" + func + "(*" + item + "))";
       // prog_args = prog + `
// try:
    // print(` + func + `(*` + item + `))
// except Exception as err:
    // print(repr(err))`
       console.log(prog_args);
       var myPromise = Sk.misceval.asyncToPromise(function() {
           return Sk.importMainWithBody("<stdin>", false, prog_args, true);
       });
       myPromise.then(function(mod) {
           results.push('success');
           console.log('success');
           //console.log(document.getElementById("output").innerHTML);
      },
           function(err) {
           results.push(err.toString() + '\n');
           console.log(err.toString());
           /*document.getElementById("output").innerHTML += err.toString() + '\n';*/
       });
   };

   // Wait for async run to finish
   setTimeout(function(){
       //Write results in console
       var final_results = [];
       var correct_items = 0;
       console.log(results);
       console.log(results.length);
       console.log(correct_results);
       for (i = 0; i < args.length; i++) {
               console.log(results[0])
           if (results[i] == 'success') {
               final_results.push(correct_results[correct_items]);
               correct_items++;
           } else {
               final_results.push(results[i]);
           }
       }
       console.log(final_results);
       // Empty correct_results
       correct_results = []
       mypre.innerHTML = final_results.join('');

       // Evaluate results
       seconds_end_page = performance.now()
       seconds_in_page = Math.round((seconds_end_page - seconds_begin_page)/1000);
       console.log("seconds in page:" + seconds_in_page);
       evaluate(args, expected_results);
       }, 2000);
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

try {
// Set pretty Python editor
    var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    mode: {name: "python",
        version: 2,
        singleLineStringErrors: false},
    lineNumbers: true,
    indentUnit: 4,
    tabMode: "spaces",
    matchBrackets: true,
    extraKeys: { Tab: betterTab },
    theme: "paraiso-dark"
    });
    editor.setSize('100%',300)
} catch {}

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
var first_keydown= true;

// When user starts typing
$('.CodeMirror').keydown(function(){

    //Starting to type for the first time
    if (seconds_to_begin == 0) {
        seconds_to_begin = Math.round((performance.now() - seconds_begin_page)/1000);
        console.log("seconds to begin: " + seconds_to_begin);
    }

    // Starting code snippet
    if (first_keydown == true){
        seconds_begin_code = performance.now();
        first_keydown = false;
    };

});
// Finished code snippet. Sum time to variable.
$('.CodeMirror').keyup(function() {
    delay(function(){
        seconds_end_code = performance.now();
        console.log("seconds in this snippet:" + Math.round(
            (seconds_end_code - seconds_begin_code)/1000));
        seconds_in_code += Math.round((seconds_end_code - seconds_begin_code)/1000);
        console.log("seconds in code: " + seconds_in_code);
        first_keydown = true;
    }, 1000);
});
