# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BestJaSettings(models.TransientModel):
    _inherit = 'bestja.config.settings'

    max_skills = fields.Integer(
        string=u"Max number of skills per offer",
        help="Maximum number of skills user can choose while creating an offer"
    )
    max_wishes = fields.Integer(
        string=u"Max number of fields per offer",
        help="Maximum number of fields of activity user can choose while creating an offer"
    )

    @api.model
    def get_default_offers_values(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'max_skills': int(conf.get_param('bestja_offers.max_skills')),
            'max_wishes': int(conf.get_param('bestja_offers.max_wishes')),
        }

    @api.one
    def set_offers_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('bestja_offers.max_skills', str(self.max_skills))
        conf.set_param('bestja_offers.max_wishes', str(self.max_wishes))
