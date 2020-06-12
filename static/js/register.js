function ajax_request(function_to_active, data,url,method) {
  $.ajax({
    url: url,
    type: method,
    async: true,
    timeout: 10000,
    contentType: "application/json",
    data: JSON.stringify(data),
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
      $("#Amessage").empty().append(result_data.responseJSON.error);
      setTimeout(
          function()
          {
            $("#Amessage").empty()
          }, 2000);
    },
    success: function (result_data) {
      function_to_active(result_data);
    }
  });
  }

	$( document ).ready(function() {
		$( "#register_form" ).submit(function( event ) {
			event.preventDefault();
			register(event);
		});
	});

  function register_success(returned_data){
  window.location.href = "/login.html";
   }

   function register()
  {
    var url = "/register";
    var method ="POST";
    var function_on_success=register_success;
    var email = $("#email")[0].value;
    var password = $("#password")[0].value;
	var full_name = $("#full_name")[0].value;
    var phone_number = $("#phone_number")[0].value;
    var data = {"Email": email, "Password": password, "Name" : full_name, "Phone Number": phone_number};
    ajax_request(function_on_success,data,url,method);
  }