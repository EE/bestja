# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.collage_photo.controllers import CollagePhoto
from openerp.addons.web.controllers.main import Home


class BestjaFrontendUCWController(CollagePhoto):

    @http.route('/', auth='public', website=True)
    def list(self, **kwargs):
        return super(BestjaFrontendUCWController, self).list(**kwargs)


class BestjaFrontendWebsite(Home, BestjaFrontendUCWController):

    @http.route('/', auth='public', website=True)
    def index(self, **kwargs):
        """
        In order to see collage_photo as the homepage, one needs to overwrite
        the main page AND override the CollagePhoto controller as well.
        """
        return super(BestjaFrontendUCWController, self).list(**kwargs)
