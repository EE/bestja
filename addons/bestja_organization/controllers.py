# -*- coding: utf-8 -*-
from openerp import http

# class BestjaOrganization(http.Controller):
#     @http.route('/bestja_organization/bestja_organization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bestja_organization/bestja_organization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bestja_organization.listing', {
#             'root': '/bestja_organization/bestja_organization',
#             'objects': http.request.env['bestja_organization.bestja_organization'].search([]),
#         })

#     @http.route('/bestja_organization/bestja_organization/objects/<model("bestja_organization.bestja_organization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bestja_organization.object', {
#             'object': obj
#         })