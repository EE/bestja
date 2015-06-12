# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.website_embeded.controllers import EmbededObjectController
from openerp.addons.website.controllers.main import Website


class BestjaFrontendWebsite(Website):

    # Change controller controlling the homepage
    @http.route()
    def index(self, **kwargs):
        return EmbededObjectController().list(**kwargs)
