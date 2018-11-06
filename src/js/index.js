import Dropzone from 'dropzone'
import { btnSuccessOnSubmit } from "./btn_success_on_submit";

document.querySelectorAll(".hasSubmitButton").forEach((form) => {
  form.addEventListener("submit", btnSuccessOnSubmit);
});

Dropzone.options.partyUpload = {
  acceptedFiles: 'image/*',
  maxFilesize: 7
};
