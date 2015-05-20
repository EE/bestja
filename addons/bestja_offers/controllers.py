#-*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from openerp import http
from openerp.addons.website.models.website import slug


class Offer(http.Controller):
    @http.route('/offer/<model("offer"):offer>', auth='public', website=True)
    def offer(self, offer):
        offer = offer.sudo()
        if offer.state != 'published':
            return http.request.not_found()
        return http.request.render('bestja_offers.offer', {
            'offer': offer,
        })

    @http.route('/offer/<model("offer"):offer>/apply', auth='user', website=True)
    def apply(self, offer):
        if http.request.httprequest.method != 'POST':
            return http.local_redirect('/offer/{}'.format(slug(offer)))
        try:
            http.request.env['offers.application'].sudo().create({
                'user': http.request.env.user.id,
                'offer': offer.id,
            })
        except IntegrityError:
            # can't use the usual `http.request.env.cr` style,
            # because `env` queries db and everything explodes
            http.request._cr.rollback()
            return http.request.render('bestja_offers.duplicate_application')

        return http.local_redirect('/offer/{}/thankyou'.format(slug(offer)))

    @http.route('/offer/<model("offer"):offer>/thankyou', auth='user', website=True)
    def thankyou(self, offer):
        return http.request.render('bestja_offers.thankyou')

    @http.route(
        '/offer/<model("offer"):offer>/meeting/<any(accepted,rejected):resolution>/',
        auth='user',
        website=True,
    )
    def meeting_confirmation(self, offer, resolution, time=None):
        """
        Allow applicants to accept/reject suggested meeting times.
        """
        application = http.request.env['offers.application'].sudo().search([
            ('offer.id', '=', offer.id),
            ('user.id', '=', http.request.env.user.id),
            ('current_meeting', '=', time),
        ])
        if not application:
            return http.request.not_found()

        if resolution == 'accepted':
            application.confirm_meeting()
        else:
            application.reject_meeting()

        return http.request.render('bestja_offers.meeting_confirmation', {
            'application': application,
            'resolution': resolution,
        })
