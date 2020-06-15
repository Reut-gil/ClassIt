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
      window.location.href = "/login.html";
    },
    success: function (result_data) {
        console.log(result_data);
        $("#name")[0].value=result_data.Name;
        $("#email")[0].value=result_data.Email;
        $("#number")[0].value=result_data["Phone Number"];
        if(result_data["Institution Name"]!==null)
        {
            $("#add")[0].value=result_data.Street;
            $("#add").prop("readonly", true);
            $("#city")[0].value=result_data.City;
            $("#city").prop("readonly", true);
            $("#colla")[0].value=result_data["Institution Name"];
            $("#colla").prop("readonly", true);
            $("#profbtn").attr("disabled",true);
        }
    }
  });
  }

  $( document ).ready(function() {
    ajax_profileGetRequest();
    $( "#instForm" ).submit(function( event ) {
			event.preventDefault();
			submitinst(event);
		});

		$('#fileform').submit(function(e) {
        $(this).ajaxSubmit({
        headers: {'Authorization':Cookies.get('Authorization')},
        error: function (result_data) {
         console.log("Error from server!");
         console.log(result_data);
      },
        success: function(data)
        {
          $("#success").empty().append(data.result);
      setTimeout(
          function()
          {
            $("#success").empty()
          }, 2000);
        }
      });
        e.preventDefault();
        });
    });


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
    $("#success").empty().append(result_data.result);
    window.location.href = "/profile.html";

      setTimeout(
  function()
  {
    $("#success").empty()
  }, 2000);
    }
  });
  }

  function submitinst(event){
  		var url = "/profile";
		var method ="POST";
		var address = $("#add")[0].value;
		var colage = $("#colla")[0].value;
		var city = $("#city")[0].value;
		var data = {"Institution Name": colage, "Street": address, "City": city};
		ajax_request(null,data,url,method);
  }