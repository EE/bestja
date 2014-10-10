openerp.bestja_offers = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.bestja_offers = {};

    /* Google Maps Widget */
    instance.bestja_offers.WidgetCoordinates = instance.web.form.FormWidget.extend({
        start: function() {
            this._super();

            /* default marker location - Palace of Culture, Warsaw */
            this.default_lat = 52.231667;
            this.default_lng = 21.006389;

            this.render();
            this.initialize_googlemaps();
            this.search_button_event();
            this.marker_drag_event();
            this.notebook_fix();

            this.on("change:effective_readonly", this, this.readonly);
            this.readonly();
        },

        /* make the elements active or not,
        depending if the form is in read only mode */
        readonly: function() {

            $form = $('#location_form');
            if(this.get("effective_readonly")) {
                this.marker.setDraggable(false);
                $form.css('visibility', 'hidden');
            } else {
                this.marker.setDraggable(true);
                $form.css('visibility', 'visible');
                // Make the lat lng fields readonly
                $(".coordinate_fields input").prop('readonly', true);
            }

        },

        render: function() {
            this.$el.html(QWeb.render("WidgetCoordinates"));
        },

        initialize_googlemaps: function(){
            /* Geocoder */
            this.geocoder = new google.maps.Geocoder();

            /* Marker */
            this.marker = new google.maps.Marker({
                title: "Złap czerwony marker aby doprecyzować lokalizację"
            });

            /* Map */
            this.map = new google.maps.Map($('#map-canvas').get(0));
            this.marker.setMap(this.map);
            this.reset_position();

            /* Autocomplete */
            // Create the autocomplete object, restricting the search
            // to geographical location types.
            var this_address = $("#address").get(0);
            this.autocomplete = new google.maps.places.Autocomplete(
               this_address,
               {types: ['establishment', 'geocode']}
            );
            // When the user selects an address from the dropdown,
            // recenter the map
            var this_obj = this;
            google.maps.event.addListener(this.autocomplete, 'place_changed', function() {
                this_obj.geocode_address($(this_address).val());
                this_obj.autocomplete_fill_in_address();
            });
        },

        marker_drag_event: function() {
            obj = this;
            google.maps.event.addDomListener(this.marker, 'drag', function(){
                var position = obj.marker.getPosition();
                obj.update_fields_values(position.lat(), position.lng());
            });
            google.maps.event.addDomListener(this.marker, 'dragend', function(){
                obj.reverse_geocode_address(obj.marker.getPosition());
            });
        },

        search_button_event: function() {
            var obj = this;
            $('button#saddress').click(function(event){
                    event.preventDefault();
                    obj.geocode_address($("#address").val());
            });
        },

        geocode_address: function(address){
            obj = this;
            this.geocoder.geocode({'address': address}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    var location = results[0].geometry.location;
                    console.log(this)
                    obj.set_map_position(location.lat(), location.lng());
                    obj.update_fields_values(location.lat(), location.lng());
                    obj.update_city_district_fields(results[0]);
                }
            });
        },
        
        /* obtain from lat-lng the address and set it in the fields*/
        reverse_geocode_address: function(position){
            obj = this;
            this.geocoder.geocode({latLng: position}, function (responses){
                if (responses && responses.length > 0) {
                    obj.update_city_district_fields(responses[0]);           
                }
            });
        },
        /* updates city and district from autocomplete if possible*/
        autocomplete_fill_in_address: function(){
            this.update_city_district_fields(this.autocomplete.getPlace());
        },
       
        /* sets district and city fields*/ 
        update_city_district_fields: function(place){
            this.field_manager.set_values({"city": ''});
            this.field_manager.set_values({"district": ''});
            if (place.address_components){
                for (var i = 0; i < place.address_components.length; i++){   
                    if (place.address_components[i].types[0] == 'locality'){
                        var val = place.address_components[i]['long_name'];
                        this.field_manager.set_values({"city": val});
                    }
                    if (place.address_components[i].types[0] == 'sublocality_level_1'){
                        var val = place.address_components[i]['long_name'];
                        this.field_manager.set_values({"district": val});
                    }
                }
            }
            
        },
        /* updates city and district from autocomplete if possible*/
        autocomplete_fill_in_address: function(){
            this.update_city_district_fields(this.autocomplete.getPlace());
        },
       
        /* sets district and city fields*/ 
        update_city_district_fields: function(place){
            this.field_manager.set_values({"map_city": ''});
            this.field_manager.set_values({"map_district": ''});
            if (place.address_components){
                for (var i = 0; i < place.address_components.length; i++){   
                    if (place.address_components[i].types[0] == 'locality'){
                        var val = place.address_components[i]['long_name'];
                        this.field_manager.set_values({"map_city": val});
                    }
                    if (place.address_components[i].types[0] == 'sublocality_level_1'){
                        var val = place.address_components[i]['long_name'];
                        this.field_manager.set_values({"map_district": val});
                    }
                }
            }
            
        },

        /* updates fields with latitude and longitude*/
        update_fields_values: function(lat, lng) {
            this.field_manager.set_values({"latitude": lat, "longitude": lng});
        },

        set_map_position: function(lat, lng) {
            var location = {lat: lat, lng: lng};
            this.map.setCenter(location);
            this.marker.setPosition(location);
            this.map.setZoom(15);
        },

        /* Set to current form fields value or default */
        reset_position: function() {
            var manager = this.field_manager;
            var lat = manager.get_field_value("latitude") || this.default_lat;
            var lng = manager.get_field_value("longitude") || this.default_lng;
            this.set_map_position(lat, lng);
        },

        /*
            if the widget is in a notebook we need to trigger resize,
            after it is shown.
        */
        notebook_fix: function(){
            var notebook = this.$el.parents(".oe_notebook_page");
            if (notebook.length != 0){  // in a notebook!
                var link_id = notebook.attr("aria-labelledby");
                var obj = this;
                $("#" + link_id).click(function() {
                        google.maps.event.trigger(obj.map, 'resize');
                        obj.reset_position();
                    }
                );
            }

        },

    });

    instance.web.form.custom_widgets.add('google_maps.coordinates', 'instance.bestja_offers.WidgetCoordinates');
}
