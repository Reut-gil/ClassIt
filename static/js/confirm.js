function ajax_request(function_to_active, data,url,method) {
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
      window.location.href = "/login.html";
    },
    success: function (result_data) {
      function_to_active(result_data);
    }
  });
  }

	$( document ).ready(function() {
		$( "#submitBtn" ).unbind("click").bind("click", function(event){
			event.preventDefault();
			confirm(event);
		});
		$( "#cancelBtn" ).unbind("click").bind("click", function(event){
			event.preventDefault();
			decline(event);
		});
	});

  function confirm_success(returned_data){
  window.location.href = "/Messages.html";
   }

   function confirm()
  {
    var url = "/confirmation";
    var method ="POST";
    var function_on_success = confirm_success;
    var confirmed = true;
    var Class = $("#class")[0].value;
	var Email = $("#Email")[0].value;
    var Date = $("#date")[0].value;
    var Start = $("#Beginning")[0].value;
    var Finish = $("#End")[0].value;
    var data = {"Is confirmed": confirmed, "Class Code": Class, "Email  of Applier" : Email,
     "Date": Date,"Start Hour": Start,"Finish Hour": Finish};
    ajax_request(function_on_success,data,url,method);
  }

   function decline()
  {
    var url = "/confirmation";
    var method ="POST";
    var function_on_success = confirm_success;
    var confirmed = false;
    var Class = $("#class")[0].value;
	var Email = $("#Email")[0].value;
    var Date = $("#date")[0].value;
    var Start = $("#Beginning")[0].value;
    var Finish = $("#End")[0].value;
    var data = {"Is confirmed": confirmed, "Class Code": Class, "Email  of Applier" : Email,
     "Date": Date,"Start Hour": Start,"Finish Hour": Finish};
    ajax_request(function_on_success,data,url,method);
  }