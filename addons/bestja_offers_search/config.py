# -*- coding: utf-8 -*-
from openerp import models, api

from .search import OffersIndex


class BestJaSettings(models.TransientModel):
    _inherit = 'bestja.config.settings'

    @api.multi
    def action_reindex(self):
        """
        Delete old Whoosh index, create a new one,
        and add all published offers.
        """
        index = OffersIndex(dbname=self.env.cr.dbname)
        index.create_index()
        self.env['offer'].search([('state', '=', 'published')]).whoosh_reindex()
