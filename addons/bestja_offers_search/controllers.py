# -*- coding: utf-8 -*-
import whoosh

from openerp import http

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
