var textareas = document.getElementsByTagName("textarea");
for (var i = 0; i < textareas.length; i++) {
  textareas[i].scrollTop = textareas[i].scrollHeight;
}