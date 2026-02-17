document.addEventListener("DOMContentLoaded", function () {
  var btn = document.querySelector(".js-theme");
  if (!btn) return;

  var clone = btn.cloneNode(true);
  btn.parentNode.replaceChild(clone, btn);

  clone.addEventListener("click", function () {
    var root = document.documentElement;
    var current = root.getAttribute("data-color-mode");
    var next = current === "dark" ? "light" : "dark";
    setColorMode(next);
    localStorage._theme = next;
  });
});
