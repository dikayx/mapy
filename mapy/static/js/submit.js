document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("analyzeForm");
    const submitButton = document.getElementById("submitButton");
    const spinner = document.getElementById("spinner");

    form.addEventListener("submit", function () {
        submitButton.disabled = true;
        spinner.style.display = "inline-block";
    });
});
