$("#messages_tbody").append("<tr><td>1</td><td>2</td><td>3</td></tr>")

var data = [{name:"lol",college:"lol",date:"lol"}];
$.each(data , function(key, value) { // data must be ARRAY!
	$("#messages_tbody").append(
	"<tr><td><span><a href='confirmation.html'><i class='fa fa-envelope-o' data-bs-hover-animate='rubberBand' style='margin-left: 0px;margin-right: 5px;height: 24px;'></i></a>" + value.name + "</span></td><td><strong>" + value.college + "</strong><br></td><td>" + value.date + "</td></tr>");
});