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
    }

    var $canvas = $('#offer-map-canvas');

    if($canvas.length) {
        createGoogleMap(
            $canvas.get(0),
            {
                center: {
                    lat: $canvas.data('lat'),
                    lng: $canvas.data('lng')
                },
                zoom: 15
            },
            $canvas.data('desc')
        );
    }
})();
