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
        },

        marker_drag_event: function() {
            obj = this;
            google.maps.event.addDomListener(this.marker, 'drag', function(){
                var position = obj.marker.getPosition();
                obj.update_fields_values(position.lat(), position.lng());
            });
        },

        search_button_event: function() {
            var obj = this;
            $('button#saddress').click(function(){
                    obj.geocode_address($("#address").val());
                }
            );
        },

        geocode_address: function(address){
            obj = this;
            this.geocoder.geocode({'address': address}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    var location = results[0].geometry.location;
                    console.log(this)
                    obj.set_map_position(location.lat(), location.lng());
                    obj.update_fields_values(location.lat(), location.lng());
                } else {
                    alert("Geocode was not successful for the following reason: " + status);
                }
            });
        },

        /* updates fields with latitude and longitude*/
        update_fields_values: function(lat, lng) {
            this.field_manager.set_values({"latitude": lat, "longitude": lng});
        },

        set_map_position: function(lat, lng) {
            var location = {lat: lat, lng: lng};
            this.map.setCenter(location);
            this.marker.setPosition(location);
            this.map.setZoom(10);
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
