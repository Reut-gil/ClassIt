function ajax_request(data,url,method) {
  $.ajax({
    url: url,
    type: method,
    async: true,
    headers: {'Authorization':Cookies.get('Authorization')},
    timeout: 2000,
    contentType: "application/json",
    data: JSON.stringify(data),
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
      $("#Amessage").empty().append(result_data.result);
    },
    success: function (result_data) {
    $("#Amessage").empty().append(result_data.result);
      setTimeout(
  function()
  {
    window.location.href = "/profile.html";
  }, 2000);
    }
  });
  }

  $( document ).ready(function() {
    ajax_profileGetRequest();
    $( "#contactForm" ).submit(function( event ) {
			event.preventDefault();
			submit(event);
		});
		});

		function ajax_profileGetRequest() {
  $.ajax({
    url: "/profile",
    type: "GET",
    async: true,
    headers: {'Authorization':Cookies.get('Authorization')},
    timeout: 2000,
    contentType: "application/json",
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
    },
    success: function (result_data) {
        $("#name")[0].value=result_data.Name;
        $("#email")[0].value=result_data.Email;
        $("#phone")[0].value=result_data["Phone Number"];
    }
  });
  }

  function submit(event)
  {
    var name = $("#name")[0].value;
    var email = $("#email")[0].value;
    var phoneNumber = $("#phone")[0].value;
    var message = $("#message")[0].value;
    var data = {"Name": name, "Email": email, "Phone Number": phoneNumber , "Subject": "", "Text":message};
    ajax_request(data,"/contact","POST")
  }