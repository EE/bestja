# -*- coding: utf-8 -*-
# from openerp import http

# class BestjaOffers(http.Controller):
#     @http.route('/bestja_offers/bestja_offers/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bestja_offers/bestja_offers/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bestja_offers.listing', {
#             'root': '/bestja_offers/bestja_offers',
#             'objects': http.request.env['bestja_offers.bestja_offers'].search([]),
#         })

#     @http.route('/bestja_offers/bestja_offers/objects/<model("bestja_offers.bestja_offers"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bestja_offers.object', {
#             'object': obj
#         })
