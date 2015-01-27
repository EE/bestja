# -*- coding: utf-8 -*-
from openerp import http


class OffersByCategory(http.Controller):
    @http.route('/offers/category/<category_slug>', auth='public', website=True)
    def offers(self, category_slug):
        if category_slug is not None:
            category = http.request.env['bestja.offer_category'].search([
                ('slug', '=', category_slug),
            ])
            if not category:
                return http.request.not_found()
        else:
            category = None

        offers = http.request.env['offer'].sudo().search([
            ('state', '=', 'published'),
            ('category.slug', '=?', category_slug),
        ])

        return http.request.render('bestja_offers_categorization.list', {
            'offers': offers,
            'category': category,
        })

    @http.route('/offers/category/', auth='public', website=True)
    def offers_all(self):
        return self.offers(category_slug=None)
