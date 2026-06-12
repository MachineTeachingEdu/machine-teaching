(function () {
    const fields = document.querySelectorAll("[data-overcode-auto-submit='true']");

    fields.forEach(function (field) {
        field.addEventListener("change", function () {
            if (field.form) {
                field.form.submit();
            }
        });
    });
})();
