# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Company(models.Model):
    """
    Add global configuration options to the company object (any other ideas?)
    """
    _inherit = 'res.company'

    bestja_max_skills = fields.Integer(default=3)
    bestja_max_wishes = fields.Integer(default=3)


class HrConfigSettings(models.TransientModel):
    _inherit = 'hr.config.settings'

    max_skills = fields.Integer(
        string="Max number of skills per offer",
        help="Maximum number of skills chosen for a single offer"
    )
    max_wishes = fields.Integer(
        string="Max number of fields per offer",
        help="Maximum number of fields of activity chosen for a single offer"
    )

    @api.model
    def get_default_values(self, fields):
        company = self.env.user.company_id
        return {
            'max_skills': company.bestja_max_skills,
            'max_wishes': company.bestja_max_wishes,
        }

    @api.one
    def set_values(self):
        company = self.env.user.company_id
        company.bestja_max_skills = self.max_skills
        company.bestja_max_wishes = self.max_wishes
