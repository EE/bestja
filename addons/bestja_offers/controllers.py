#-*- coding: utf-8 -*-
import whoosh

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
        return http.request.render('bestja_offers.offer', {
            'offer': offer,
        })

    @http.route(
        '/offer/<model("offer"):offer>/apply',
        auth='user',
        methods=['POST']
    )
    def apply(self, offer):
        http.request.env['offers.application'].create({
            'user': http.request.env.user.id,
            'offer': offer.id,
        })
        return http.local_redirect('/offer/{}/thankyou'.format(slug(offer)))

    @http.route('/offer/<model("offer"):offer>/thankyou', auth='user', website=True)
    def thankyou(self, offer):
        return http.request.render('bestja_offers.thankyou')
