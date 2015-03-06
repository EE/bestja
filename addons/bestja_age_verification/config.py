# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BestJaSettings(models.TransientModel):
    _inherit = 'bestja.config.settings'

    min_age = fields.Integer(
        string=u"Minimalny wiek",
    )

    @api.model
    def get_default_age_values(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'min_age': int(conf.get_param('bestja_age_verification.min_age')),
        }

    @api.one
    def set_age_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('bestja_age_verification.min_age', str(self.min_age))
