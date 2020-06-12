function ajax_request(function_to_active, data,url,method) {
  $.ajax({
    url: url,
    type: method,
    async: true,
    timeout: 10000,
    beforeSend: function(request) {
    },
    contentType: "application/json",
    data: JSON.stringify(data),
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
      $("#Amessage").empty().append("invalid email or password");
      setTimeout(
  function()
  {
    $("#Amessage").empty()
  }, 3000);
    },
    success: function (result_data) {
        Cookies.set('Authorization',"Bearer " +result_data.data);
        window.location.href = "/Home.html";
    }
  });
  }
  
	$( document ).ready(function() {
		$( "#login_form" ).submit(function( event ) {
			event.preventDefault();
			login(event);
		});

	});

	function login(event)
	{
		var url = "/login";
		var method ="POST";
		var email = $("#email")[0].value;
		var password = $("#password")[0].value;
		var data = {"Email": email, "Password": password};
		ajax_request(null,data,url,method);
	}

