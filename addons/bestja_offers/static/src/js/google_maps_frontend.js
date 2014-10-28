(function () {
    "use strict";
    if (typeof google == 'undefined') {
        return;
    }

    function createGoogleMap (element, mapOptions, infoWindowContent) {

        var map = new google.maps.Map(element, mapOptions);

        var marker = new google.maps.Marker({});
        marker.setMap(map);
        marker.setPosition(mapOptions.center);

        var infowindow = new google.maps.InfoWindow({
            content: infoWindowContent
        });
        google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map, marker);
        });
        return map;
    };

    var $locationElement = $('#bestja_offers_offer_location');

    createGoogleMap(
        document.getElementById('offer-map-canvas'),
        {
            center: {
                lat: $locationElement.data('lat'),
                lng: $locationElement.data('lng')
            },
            zoom: 15
        },
        // TODO this is only mock. Get data from backend.
        'Laboratorium EE<br />Szpitalna 8A / 3 <br />(testowy adres)'
    );

})();
