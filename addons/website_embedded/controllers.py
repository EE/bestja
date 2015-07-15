# -*- coding: utf-8 -*-
from openerp import http

from .models import EmbeddedObject


class EmbeddedObjectController(http.Controller):
    @http.route('/embedded/', auth='public', website=True)
    def list(self, template='website_embedded.list', **kwargs):
        objects = {}
        for kind_id, _ in EmbeddedObject.KINDS:
            objects[kind_id] = http.request.env['embedded_object'].search([('kind', '=', kind_id)])

        return http.request.render(template, {
            'objects': objects,
        })

    @http.route('/embedded/<model("embedded_object"):embedded_object>', auth='public', website=True)
    def offer(self, embedded_object):
        return http.request.render('website_embedded.detail', {
            'object': embedded_object,
        })
