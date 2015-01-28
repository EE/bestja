# -*- coding: utf-8 -*-
from openerp import http


class OffersByOrg(http.Controller):
    @http.route('/offers/organization/<city_slug>', auth='public', website=True)
    def offer(self, city_slug=None):
        if not city_slug:
            return http.request.not_found()

        if city_slug == 'root':
            organization = http.request.env['organization'].sudo().search([
                ('level', '=', 0),
            ])
        else:
            organization = http.request.env['organization'].sudo().search([
                ('level', '=', 1),
                ('city_slug', '=', city_slug)
            ])
        if not organization:
            return http.request.not_found()

        if city_slug == 'root':
            offers = http.request.env['offer'].sudo().search([
                ('state', '=', 'published'),
                ('project.organization', '=', organization.id),
            ])
        else:
            offers = http.request.env['offer'].sudo().search([
                ('state', '=', 'published'),
                '|',  # noqa
                    ('project.organization', '=', organization.id),
                    ('project.organization.parent', '=', organization.id),
            ])

        return http.request.render('bestja_offers_by_org.list', {
            'offers': offers,
            'organization': organization,
        })
