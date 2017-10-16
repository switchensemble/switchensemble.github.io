var geocoder;
var map;
var mapOptions = {
    zoom: 15,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }
var marker;

function initialize() {
  geocoder = new google.maps.Geocoder();
  map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
  codeAddress();
}

function codeAddress() {
  var address = document.getElementById('address').value;
  geocoder.geocode( { 'address': address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
      if(marker)
        marker.setMap(null);
      marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location,
          draggable: true
      });
      google.maps.event.addListener(marker, "dragend", function() {
        document.getElementById('lat').value = marker.getPosition().lat();
        document.getElementById('lng').value = marker.getPosition().lng();
      });
      document.getElementById('lat').value = marker.getPosition().lat();
      document.getElementById('lng').value = marker.getPosition().lng();
    } else {
      // alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}

$(document).ready(function(){
  initialize();
});
