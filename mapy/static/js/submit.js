document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("analyzeForm");
    const submitButton = document.getElementById("submitButton");
    const spinner = document.getElementById("spinner");

    form.addEventListener("submit", function () {
        // Disable the submit button to prevent multiple submissions
        submitButton.disabled = true;

        // Show the spinner
        spinner.style.display = "inline-block";

        console.log("Form submitted");
    });
});
