openerp.bestja_offers = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var map;

    instance.bestja_offers = {};

    instance.bestja_offers.WidgetCoordinates = instance.web.form.FormWidget.extend({
        start: function() {
            this._super();
            this.$el.css("width", "600px");
            this.$el.css("height", "300px");
            this.set_default_coordinates();
            this.initialize_geocoder_marker();
            this.display_map();
            //search button
            var this_obj = this;
            $('button#saddress').click(
                function(){
                    this_obj.get_geocoder(this_obj);
                }
            );
        },

        initialize_geocoder_marker: function(){
            this.geocoder = new google.maps.Geocoder();
            this.marker = new google.maps.Marker({
                position: new google.maps.LatLng(this.default_lat, this.default_lng),
                title:"Złap czerwony marker aby doprecyzować lokalizację",
                draggable:true,
            });
        },

        /* Those two functions are for event when button "szukaj" is clicked*/
        get_geocoder: function(obj){
            var adr = $("#address").val();
            console.log(adr);
            obj.geocode_address(adr);
        },


        geocode_address: function(address){
            var mark = this.marker;
            var this_obj = this;
            this.geocoder.geocode( { 'address': address}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                        map.setCenter(results[0].geometry.location);
                        mark.setPosition(results[0].geometry.location);
                        map.setZoom(10);
                        var lat = results[0].geometry.location.lat();
                        var lng = results[0].geometry.location.lng();
                        this_obj.reset_coordinates(lat, lng);
                        this_obj.update_fields_values(lat, lng);
                } else {
                alert("Geocode was not successful for the following reason: " + status);
                }
            });
            console.log("new address set");
        },

        /* Main function for displaying map*/
        display_map: function(){
            this.$el.html(QWeb.render("WidgetCoordinates", {
                    "latitude": this.field_manager.get_field_value("provider_latitude") || 0,
                    "longitude": this.field_manager.get_field_value("provider_longitude") || 0,
                    }));
            var mapOptions = {
                zoom: 10,
                center: new google.maps.LatLng(this.default_lat, this.default_lng)
            }

            map = new google.maps.Map(this.$('#map-canvas').get(0),
                        mapOptions);

            /* to recenter the map when it's loaded second time*/
            google.maps.event.addDomListener(this.$('#map-canvas'), 'resize', function() {
                map.setCenter({lat: default_lat, lng: default_lng});
            });


            this.marker.setMap(map);
            var marker = this.marker;
            var this_obj = this;
            google.maps.event.addDomListener(marker, 'drag', function(){
                var lt = marker.getPosition().lat();
                var lng = marker.getPosition().lng();
                this_obj.reset_coordinates(lt, lng);
                this_obj.update_fields_values(lt, lng);
            });
            this.recenter_map();
        },

        /* updates fields with latitude and longitude*/
        update_fields_values: function(lat, lng){
            this.field_manager.set_values({"provider_latitude": lat, "provider_longitude": lng});
        },
        /* default value for map centering - Palace of Culture, Warsaw*/
        set_default_coordinates: function(){
            this.default_lat = 52.231667;
            this.default_lng = 21.006389;
        },

        /* for resetting default coordinates*/
        reset_coordinates: function(lt, lng) {
            this.default_lat =  lt;
            this.default_lng = lng;
            console.log(lt + " " + lng);
        },

        /* pages in notebook are labeled by links, we're getting links here
                and triggering the map to reload when the tab is opened*/
        recenter_map: function(){
            var prnt = this.$el.parents(".oe_notebook_page");
            if (prnt.length != 0){
                var new_latitude = this.field_manager.get_field_value("provider_latitude") ||
                                        this.default_lat;
                var new_longitude = this.field_manager.get_field_value("provider_longitude") ||
                                        this.default_lng;
                var link_id = prnt.attr("aria-labelledby");
                $("#"+link_id).click(
                    function() {
                        google.maps.event.trigger(map, 'resize');
                        map.setCenter({lat: new_latitude, lng: new_longitude});
                        }
                );
            }

        },

    });

    instance.web.form.custom_widgets.add('google_maps.coordinates', 'instance.bestja_offers.WidgetCoordinates');
}
