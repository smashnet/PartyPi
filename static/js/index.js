$(document).ready(function() {

$("#get-data").click(function(e) {
  $.get("/weather", function(data) {
    $("#result").val(data);
  });
});

});
