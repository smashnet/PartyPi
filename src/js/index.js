import Dropzone from 'dropzone'
import Siema from 'siema'
import { btnSuccessOnSubmit } from "./btn_success_on_submit";
import { deleteData } from "./delete_request";
import { openFullscreen, closeFullscreen } from "./fullscreen";

window.deleteData = deleteData
window.openFullscreen = openFullscreen
window.closeFullscreen = closeFullscreen
window.Siema = Siema

document.querySelectorAll(".hasSubmitButton").forEach((form) => {
  form.addEventListener("submit", btnSuccessOnSubmit);
});

Dropzone.options.partyUpload = {
  acceptedFiles: 'image/*',
  maxFilesize: 7
};
