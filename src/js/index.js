import Dropzone from 'dropzone'
import { btnSuccessOnSubmit } from "./btn_success_on_submit";
import { deleteData } from "./delete_request";

window.deleteData = deleteData

document.querySelectorAll(".hasSubmitButton").forEach((form) => {
  form.addEventListener("submit", btnSuccessOnSubmit);
});

Dropzone.options.partyUpload = {
  acceptedFiles: 'image/*',
  maxFilesize: 7
};
