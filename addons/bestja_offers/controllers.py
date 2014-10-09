#-*- coding: utf-8 -*-
from openerp import http

import search


class Search(http.Controller):
    @http.route('/search/', auth='public', website=True)
    def profile(self, q='', **kwargs):
        if q:
            query = search.get_parser().parse(q)
            index = search.get_index()
            with index.searcher() as s:
                reply = s.search(query)
                # Need to evaluate the results now,
                # while the searcher is still open
                results = [hit.fields() for hit in reply]
                count = len(reply)
        else:
            results = None
            count = 0

        return http.request.render('bestja_offers.search', {
            'results': results,
            'count': count,
            'q': q,
        })
