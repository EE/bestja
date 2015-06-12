# -*- coding: utf-8 -*-
from openerp import http

from .models import EmbededObject


class EmbededObjectController(http.Controller):
    @http.route('/embeded/', auth='public', website=True)
    def list(self, **kwargs):
        objects = {}
        for kind_id, _ in EmbededObject.KINDS:
            objects[kind_id] = http.request.env['embeded_object'].search([('kind', '=', kind_id)])

        return http.request.render('website_embeded.list', {
            'objects': objects,
        })

    @http.route('/embeded/<model("embeded_object"):embeded_object>', auth='public', website=True)
    def offer(self, embeded_object):
        return http.request.render('website_embeded.detail', {
            'object': embeded_object,
        })
