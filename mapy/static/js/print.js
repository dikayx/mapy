document.addEventListener("DOMContentLoaded", function () {
    document
        .getElementById("download-pdf")
        .addEventListener("click", function () {
            window.print();
        });
});
