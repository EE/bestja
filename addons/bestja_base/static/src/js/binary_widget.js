openerp.bestja_base = function(instance) {
    
    /* Raise the upload file limit to 300 MB */
    instance.web.form.FieldBinary.include({
        init: function(field_manager, node) {
            this._super(field_manager, node);
            this.max_upload_size = 300 * 1024 * 1024; // 300 Mb
        }
    });
}
