# -*- coding: utf-8 -*-

from openerp import models, fields, api

from .search import OffersIndex


class Company(models.Model):
    """
    Add global configuration options to the company object (any other ideas?)
    """
    _inherit = 'res.company'

    bestja_max_skills = fields.Integer(default=3, string="Max number of skills to be chosen per offer")
    bestja_max_wishes = fields.Integer(default=3, string="Max number of fields of activity to be chosen per offer")


class BestJaSettings(models.TransientModel):
    _inherit = 'bestja.config.settings'

    max_skills = fields.Integer(
        string="Max number of skills per offer",
        help="Maximum number of skills user can choose while creating an offer"
    )
    max_wishes = fields.Integer(
        string="Max number of fields per offer",
        help="Maximum number of fields of activity user can choose while creating an offer"
    )

    @api.model
    def get_default_offers_values(self, fields):
        company = self.env.user.company_id
        return {
            'max_skills': company.bestja_max_skills,
            'max_wishes': company.bestja_max_wishes,
        }

    @api.one
    def set_offers_values(self):
        company = self.env.user.company_id
        company.bestja_max_skills = self.max_skills
        company.bestja_max_wishes = self.max_wishes

    @api.multi
    def action_reindex(self):
        """
        Delete old Whoosh index, create a new one,
        and add all published offers.
        """
        index = OffersIndex(dbname=self.env.cr.dbname)
        index.create_index()
        self.env['offer'].search([('state', '=', 'published')]).whoosh_reindex()
