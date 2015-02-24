# -*- coding: utf-8 -*-
from openerp import http


class CollagePhoto(http.Controller):

    @http.route('/collage_photo/', auth='public', website=True)
    def list(self, **kwargs):
        return http.request.render('collage_photo.listing', {
            'photos': http.request.env['collage_photo'].search([]),
        })
