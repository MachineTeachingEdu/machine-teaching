// output functions are configurable.  This one just appends some text
// to a pre element.
function outf(text) {
    var mypre = document.getElementById("output");
    mypre.innerHTML = mypre.innerHTML + text;
}
function builtinRead(x) {
    if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined)
            throw "File not found: '" + x + "'";
    return Sk.builtinFiles["files"][x];
}

function evaluate(expected_results){
    eval_div = document.getElementById("evaluation");
    eval_div.innerHTML = "";
    answers = document.getElementById("output").innerHTML.split("\n");
    errors = 0;

    // For each test, compare results
    for (i = 0; i < expected_results.length; i++){
        console.log(answers[i]);
        try {
            answers_parsed = JSON.parse(answers[i].replace(/'/g, '"'));
        }
        catch(e) {
            answers_parsed = answers[i];
        }
        console.log(answers_parsed)
        try {
            expected_results_parsed = JSON.parse(expected_results[i].replace(/'/g, '"'));
        } catch(e) {
            expected_results_parsed = expected_results[i];
        }
        console.log(expected_results_parsed);
        eval_div.innerHTML += "Expected output: " + expected_results[i] + "<br>" + "Your output: " + answers[i] + "<br>";
        if (JSON.stringify(expected_results_parsed, Object.keys(expected_results_parsed).sort()) == JSON.stringify(answers_parsed, Object.keys(answers_parsed).sort())){
        //if (JSON.stringify(expected_results[i]) == JSON.stringify(answers[i])){
            eval_div.innerHTML += '<span class="badge badge-success">OK</span><br><br>'
        } else {
            eval_div.innerHTML += '<span class="badge badge-danger">OOPS!</span><br><br>'
            errors++;
        };
    }

    // If no errors are found, go to the next problem
    if (errors == 0) {
        document.getElementById("next").style.background = 'green';
        document.getElementById("next").innerHTML = "Next";
        document.getElementById("next").onclick = gotoproblem;
        save_log('P', seconds_in_code, seconds_to_begin, seconds_in_page);
    } else {
        save_log('F', seconds_in_code, seconds_to_begin, seconds_in_page);
    };
}
// Here's everything you need to run a python program in skulpt
// grab the code from your textarea
// get a reference to your pre element for output
// configure the output function
// call Sk.importMainWithBody()
function runit(args, func, expected_results) {
   // Display result divs
   document.getElementById("output-div").style.display="block";
   document.getElementById("testcase-div").style.display="block";

   // Get code
   var prog = editor.getValue();

   // Prepare output display
   var mypre = document.getElementById("output");
   mypre.innerHTML = '';
   Sk.pre = "output";
   Sk.configure({output:outf, read:builtinRead});
   (Sk.TurtleGraphics || (Sk.TurtleGraphics = {})).target = 'mycanvas';

   console.log(args);
   for (i = 0; i < args.length; i++) {
       item = args[i];
       console.log(item);
       prog_args = prog + "\nprint(" + func + "(*" + JSON.stringify(item) + "))";
       console.log(prog_args);
       var myPromise = Sk.misceval.asyncToPromise(function() {
           return Sk.importMainWithBody("<stdin>", false, prog_args, true);
       });
       myPromise.then(function(mod) {
           console.log('success');
           console.log(document.getElementById("output").innerHTML);
      },
           function(err) {
           console.log(err.toString());
           document.getElementById("output").innerHTML = err.toString();
       });
   };

   // Evaluate results
   seconds_end_page = performance.now()
   seconds_in_page = Math.round((seconds_end_page - seconds_begin_page)/1000);
   console.log("seconds in page:" + seconds_in_page);
   evaluate(expected_results);
};

function skipit() {
   // Evaluate results
   seconds_end_page = performance.now()
   seconds_in_page = Math.round((seconds_end_page - seconds_begin_page)/1000);
   console.log("seconds in page:" + seconds_in_page);
   console.log("seconds to begin: " + seconds_to_begin);
   console.log("seconds in code:" + seconds_in_code);

   save_log('S', seconds_in_code, seconds_to_begin, seconds_in_page);

   setTimeout(function(){
       gotoproblem();
   }, 2000);
};

function gotoproblem() {
     location.reload();
}

function betterTab(cm) {
    if (cm.somethingSelected()) {
        cm.indentSelection("add");
    } else {
        cm.replaceSelection(cm.getOption("indentWithTabs")? "\t":
                Array(cm.getOption("indentUnit") + 1).join(" "), "end", "+input");
    }
}

// Set pretty Python editor
var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
mode: {name: "python",
    version: 2,
    singleLineStringErrors: false},
lineNumbers: true,
indentUnit: 4,
tabMode: "spaces",
matchBrackets: true,
extraKeys: { Tab: betterTab }
});

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
