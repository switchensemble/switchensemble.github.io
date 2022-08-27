audiojs.events.ready(function() {
	var as = audiojs.createAll();
});

var i = 0;
setInterval(function($){
		var a = ["assets/images/switch-home.jpg", "assets/images/walton-crossing_bg.jpg", "assets/images/sheehan-the-bends_bg.jpg"], newdoc = $("<div class='bgimg' style='display:none;'></div>");
		i = (i > (a.length - 1))?0:i;
		//with jquery

		$(".bgimg").fadeOut(300, function() {  $(this).remove(); newdoc.appendTo("body").css("background-image", "url('" + a[i++] + "')").fadeIn(300);});

	 //with pure javascript
	 // document.body.style.backgroundImage = "url('" + a[i++] + "')";
}, 5000,$);
