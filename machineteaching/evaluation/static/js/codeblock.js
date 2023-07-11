function betterTab(cm) {
    if (cm.somethingSelected()) {
        cm.indentSelection("add");
    } else {
        cm.replaceSelection(cm.getOption("indentWithTabs")? "\t":
                Array(cm.getOption("indentUnit") + 1).join(" "), "end", "+input");
    }
}

codes = document.getElementsByName("code");
for (i in codes) {
    // Set pretty Python editor
    var editor = CodeMirror.fromTextArea(codes[i], {
    mode: {name: "python",
        version: 2,
        singleLineStringErrors: false},
    lineNumbers: true,
    indentUnit: 4,
    tabMode: "spaces",
    matchBrackets: true,
    extraKeys: { Tab: betterTab }
    });
};
