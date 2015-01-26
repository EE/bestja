# -*- coding: utf-8 -*-
from openerp import http


class OffersByOrg(http.Controller):
    @http.route('/offers/organization/<city_slug>', auth='public', website=True)
    def offer(self, city_slug=None):
        if not city_slug:
            return http.request.not_found()

        if city_slug == 'root':
            offers = http.request.env['offer'].sudo().search([
                ('state', '=', 'published'),
                ('project.organization.level', '=', 0),
            ])
        else:
            offers = http.request.env['offer'].sudo().search([
                ('state', '=', 'published'),
                ('project.organization.level', '!=', 0),
                '|',  # noqa
                    ('project.organization.city_slug', '=', city_slug),
                    ('project.organization.parent.city_slug', '=', city_slug),
            ])

        return http.request.render('bestja_offers_by_org.list', {
            'offers': offers,
        })
