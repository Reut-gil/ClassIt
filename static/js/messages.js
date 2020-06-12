function ajax_messegesGetRequest() {
  $.ajax({
    url: "/confirmation",
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
        console.log(result_data);
        $.each(result_data["results"] , function(key, value) {
        $("#messages_tbody").append(
        "<tr>" +
            "<td><span><a href='confirmation.html'><i class='fa fa-envelope-o' data-bs-hover-animate='rubberBand' style='margin-left: 0px;margin-right: 5px;height: 24px;'></i></a>"+ value[key]["Name"] + "</span></td>"+
                "<td>"+ value[key]["Building Name"] +"</td>"+
                "<td>"+ value[key]["Class Code"] +"</td>"+
                "<td>"+ value[key]["Start Hour"] +"</td>"+
                "<td>"+ value[key]["Finish Hour"] +"</td>"+
                "<td>"+ value[key]["Date"] +"</td>"+
                "<td id="+"td"+key+"><i id="+ value[key]["_id"] +" class='fa fa-check-circle' data-bs-hover-animate='rubberBand'style='margin-left: 0px;margin-right: 5px;height: 24px;font-size: 26px;color: rgb(25,50,237);'></i><i id="+ value[key]["_id"] +" class='fa fa-times-circle'data-bs-hover-animate='rubberBand' style='margin-left: 0px;margin-right: 5px;height: 24px;font-size: 26px;color: rgb(254,19,4);'></i>"+
             "</td>"+
        "</tr>")
        if(value[key]["IsApproved"])
        {
            $("#td"+key).remove();
        }
        });
        $('[data-bs-hover-animate]')
		.mouseenter( function(){ var elem = $(this); elem.addClass('animated ' + elem.attr('data-bs-hover-animate')) })
		.mouseleave( function(){ var elem = $(this); elem.removeClass('animated ' + elem.attr('data-bs-hover-animate')) });
		$(".fa-check-circle")
		.click(confirm);
		$(".fa-times-circle")
		.click(decline);
    }
  });
  }
    $( document ).ready(function() {
    ajax_messegesGetRequest();
    });

   function confirm(e){
        console.log(e.target.id)
        $.ajax({
    url: "/confirmation",
    type: "POST",
    async: true,
    headers: {'Authorization':Cookies.get('Authorization')},
    timeout: 10000,
    contentType: "application/json",
    data: JSON.stringify({"Is confirmed":true,"_id":e.target.id}),
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
    },
    success: function (result_data) {
        console.log(result_data);
        window.location.href = "/Messages.html";
    }
  });
   }

   function decline(e){
        console.log(e.target.id)
        $.ajax({
    url: "/confirmation",
    type: "POST",
    async: true,
    headers: {'Authorization':Cookies.get('Authorization')},
    timeout: 10000,
    contentType: "application/json",
    data: JSON.stringify({"Is confirmed":false,"_id":e.target.id}),
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
    },
    success: function (result_data) {
        console.log(result_data);
        window.location.href = "/Messages.html";
    }
  });
   }