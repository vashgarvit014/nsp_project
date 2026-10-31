document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".auto-dismiss").forEach(function (el) {
        setTimeout(function () {
            el.classList.remove("show");
        }, 4000);
    });
});
