openerp.bestja_volunteer = function(instance) {
    /*
    Form widget for one2many, many2many and many2one fields, that
    (instead of rendering the field) redirects the user to the related
    object's page.
    */
    instance.bestja_volunteer.RedirectWidget = instance.web.form.AbstractField.extend({
        start: function() {
            this._super();
            value = this.get("value");
            if($.isArray(value)) {
                if(value.length == 0) {
                    return;
                }
                value = value[0]
            }
            if(value === false) {
                return;
            }
            var context = this.build_context().eval();
            var model_obj = new instance.web.Model(this.field.relation);
            self = this;
            model_obj.call('get_formview_action', [value, context]).then(function(action){
                self.do_action(action);
            });
        }
    });
    instance.web.form.widgets.add('x2x_redirect', 'instance.bestja_volunteer.RedirectWidget');
}
