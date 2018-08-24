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
    for (i = 0; i < expected_results.length; i++){
        eval_div.innerHTML += "Expected output: " + expected_results[i] + "<br>" + "Your output: " + answers[i] + "<br>";
        if (JSON.stringify(expected_results[i]) == JSON.stringify(answers[i])){
            eval_div.innerHTML += '<span style="color:green">OK</span><br><br>'
        } else {
            eval_div.innerHTML += '<span style="color:red">OOPS!</span><br><br>'
        };
    }

//    if errors == 0{
//        console.log(document.getElementById("next").style);
//    }
}
// Here's everything you need to run a python program in skulpt
// grab the code from your textarea
// get a reference to your pre element for output
// configure the output function
// call Sk.importMainWithBody()
function runit(args, func, expected_results) {
   var prog = document.getElementById("yourcode").value;

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
       });
   };

   evaluate(expected_results);
}
