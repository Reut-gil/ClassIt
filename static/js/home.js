function ajax_messegesGetRequest() {
  $.ajax({
    url: "/confirmation",
    type: "GET",
    async: true,
    headers: {'Authorization':Cookies.get('Authorization')},
    timeout: 10000,
    contentType: "application/json",
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
    },
    success: function (result_data) {
        console.log(result_data);
        var newMesseges=0;
        $.each(result_data["results"] , function(key, value) {
            if(value[key]["IsApproved"] == null)
            {
                newMesseges +=1;
            }
        });

        $("#rgreeting").text("You have "+ newMesseges +" new requests");

        }
    });
  }

  function ajax_profileGetRequest() {
  $.ajax({
    url: "/profile",
    type: "GET",
    async: true,
    headers: {'Authorization':Cookies.get('Authorization')},
    timeout: 10000,
    contentType: "application/json",
    error: function (result_data) {
      console.log("Error from server!");
      console.log(result_data);
      window.location.href = "/login.html";
    },
    success: function (result_data) {
        console.log(result_data);
        $("#ngreeting").text("Welcome "+result_data.Name+"!");
    }
  });
  }

    $( document ).ready(function() {
    ajax_profileGetRequest();
    ajax_messegesGetRequest();
    });