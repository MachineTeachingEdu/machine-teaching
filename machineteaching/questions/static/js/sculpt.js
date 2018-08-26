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
    console.log(answers);
    console.log(expected_results);

    // For each test, compare results
    for (i = 0; i < expected_results.length; i++){
        eval_div.innerHTML += "Expected output: " + expected_results[i] + "<br>" + "Your output: " + answers[i] + "<br>";
        if (JSON.stringify(expected_results[i]) == JSON.stringify(answers[i])){
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
    }
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
   evaluate(expected_results);
}

// Set pretty Python editor
var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
mode: {name: "python",
       version: 2,
       singleLineStringErrors: false},
lineNumbers: true,
indentUnit: 4,
tabMode: "shift",
matchBrackets: true
});
