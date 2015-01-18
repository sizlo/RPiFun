var textareas = document.getElementsByClassName("scrolled");
for (var i = 0; i < textareas.length; i++) {
  textareas[i].scrollTop = textareas[i].scrollHeight;
}