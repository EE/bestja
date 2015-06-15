# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.website_embedded.controllers import EmbeddedObjectController
from openerp.addons.website.controllers.main import Website


class BestjaFrontendWebsite(Website):

    # Change controller controlling the homepage
    @http.route()
    def index(self, **kwargs):
        return EmbeddedObjectController().list(**kwargs)
