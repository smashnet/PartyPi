export function btnSuccessOnSubmit() {
  var button = document.getElementById("submitButton");
  button.classList.remove('btn-primary');
  button.classList.add('btn-success');
  button.setAttribute('disabled', '');
  button.innerHTML = 'Erledigt!';
};
