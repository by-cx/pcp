if(jQuery.url.segment(1) == "invoices" && jQuery.url.segment(2) == "invoice") {
	$.ajax({
		type: "GET",
		url: "/invoices/next_payment_id/",
		success: function(msg){
			$(document).ready(function(){
				if($("#id_payment_id").val() == "0") $("#id_payment_id").val(msg);
				if($("#id_date_exposure").val() != "") {
					$('.sign').append("<div style=\"margin: 3px;\"><a href=\"/django-admin/invoices/item/add/?invoice="+$("#id_payment_id").val()+"\" class=\"add-another\" id=\"add_id_client_address\" onclick=\"return showAddAnotherPopup(this);\"> PÅ™idat poloÅ¾ku do faktury <img src=\"/media/img/admin/icon_addlink.gif\" width=\"10\" height=\"10\" alt=\"PÅ™idat poloÅ¾ku\"/></a></div>");
				}
			})
		}
	});
	$.ajax({
		type: "GET",
		url: "/invoices/items/"+jQuery.url.segment(3),
		success: function(msg){
			$(document).ready(function(){
					$('.sign').append(msg);
			})
		}
	});
	$.ajax({
		type: "GET",
		url: "/invoices/stats/",
		success: function(msg){
			$(document).ready(function(){
					$('#content').prepend(msg);
			})
		}
	});
}
//$(document).ready(function(){
//	alert(jQuery.url.attr("path"));
//})
