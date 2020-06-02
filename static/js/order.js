function ajax_classrequest(function_to_active, data,url,method) {
  $.ajax({
    url: url,
    type: method,
    async: true,
    timeout: 2000,
    contentType: "application/json",
    data: JSON.stringify(data),
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
      if(result_data.status==400)
      {
        $("#error").empty().append(result_data.responseJSON.data);
      }
      else
      {
        $("#error").empty().append("error occurred saving info");
      }
      setTimeout(
  function()
  {
    $("#error").empty()
  }, 2000);
    },
    success: function (result_data) {
      function_to_active(result_data);
      window.location.href = "/Index.html";
    }
  });
  }

  function ajax_getrequest(function_to_active,url) {
  $.ajax({
    url: url,
    type: "GET",
    async: true,
    timeout: 2000,
    contentType: "application/json",
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
    },
    success: function (result_data) {
      function_to_active(result_data);
    }
  });
  }

	$( document ).ready(function() {
		$("#applyroom").submit(function( event ) {
			event.preventDefault();
			applying_for_room(event);
		});
		ajax_getrequest(populateInst,"/applying-for-room");

   $("#dcampus a").click(function(){
      $("#cselect").text($(this).text());
      $("#cselect").val($(this).text());

   });
	});

	function populateInst(returned_data)
	{
        $.each(returned_data ,function(key, value1) {
        $.each(value1 ,function(key, value) {
        $("#dcampus").append(
        "<a class='dropdown-item' role='presentation' href='javascript:void(0)'>"+value[key]+"</a>"
        )});
	});
	      $(function(){
    $("#dcampus a").click(function(){
      $("#cselect").text($(this).text());
      $("#cselect").val($(this).text());

   });
});
}

  function order_success(returned_data){
  window.location.href = "Index.html";
   }

  function applying_for_room(event)
   {
    var url = "/applying-for-room";
    var method ="POST";
    var function_on_success=order_success;
    var email = $("#Email")[0].value;
    var date = $("#date")[0].value;
	var full_name = $("#Name")[0].value;
    var phone_number = $("#Phone_Number")[0].value;
    var Start = $("#begin")[0].value;
    var finish = $("#end")[0].value;
    var NumberOfClass = $("#nselect")[0].value;
    var NumberOfseats = $("#numOfStudents")[0].value;
    var Projector = $("#ProjectorCheck")[0].checked;
    var Accessibility = $("#AccessibilityCheck")[0].checked;
    var Computers = $("#ComputersLaboratoryCheck")[0].checked;
    var Institution = $("#cselect")[0].value;
    var data = {"Email": email,"Date": date, "Name" : full_name, "Phone Number": phone_number,
    "Start Hour":Start,"Finish Hour":finish,"Number of Classes":parseInt(NumberOfClass),"Number of Seats":parseInt(NumberOfseats),
    "Projector":Projector,"Accessibility":Accessibility,"Computers":Computers,"Institution": Institution};
    ajax_classrequest(function_on_success,data,url,method);
  }



  $(function(){
    $("#dnumber a").click(function(){
      $("#nselect").text($(this).text());
      $("#nselect").val($(this).text());

   });
});