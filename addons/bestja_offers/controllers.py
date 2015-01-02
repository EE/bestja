#-*- coding: utf-8 -*-
import whoosh
from psycopg2 import IntegrityError

from openerp import http
from openerp.addons.website.models.website import slug

from .search import OffersIndex, OffersFacets


class Search(http.Controller):
    @http.route('/search/', auth='public', website=True)
    def search(self, q='', **kwargs):
        # Get params as a real MultiDict
        args = http.request.httprequest.args
        index = OffersIndex(dbname=http.request.session.db)

        if q:
            query = index.get_parser().parse(q)
        else:
            query = whoosh.query.Every()  # Get all results

        facets = OffersFacets()

        with index.get_index().searcher() as s:
            response = s.search(
                query,
                groupedby=facets.facets,
                filter=facets.get_filter(args),
            )

            # Need to evaluate the results now,
            # while the searcher is still open
            results = [hit.fields() for hit in response]

            return http.request.render('bestja_offers.search', {
                'results': results,
                'facets': facets.facets_with_groups(response, args),
                'count': len(response),
                'q': q,
            })


class Offer(http.Controller):
    @http.route('/offer/<model("offer"):offer>', auth='public', website=True)
    def offer(self, offer):
        offer = offer.sudo()
        if offer.state != 'published':
            return http.request.not_found()
        return http.request.render('bestja_offers.offer', {
            'offer': offer,
        })

    @http.route('/offer/<model("offer"):offer>/apply', auth='user')
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
            # Unique constraint.
            # Should this redirect user to a page with a different message?

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

        application.current_meeting_state = resolution

        application.send(
            template='bestja_offers.msg_application_meeting_' + resolution,
            recipients=application.offer.project.responsible_user,
            sender=http.request.env.user,
        )

        return http.request.render('bestja_offers.meeting_confirmation', {
            'application': application,
            'resolution': resolution,
        })
