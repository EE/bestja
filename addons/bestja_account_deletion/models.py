# -*- coding: utf-8 -*-

from openerp import models, fields, api
import uuid


class Volunteer(models.Model):
    _inherit = 'res.users'

    active_state = fields.Selection(selection_add=[('deleted', 'usunięty')])
    reason_for_deleting_account = fields.Text()

    @api.one
    def delete_account(self):
        self.write({'login': uuid.uuid1(),
                    'name': 'Konto usunięte',
                    'street_gov': '',
                    'street_number_gov': '',
                    'apt_number_gov': '',
                    'zip_code_gov': '',
                    'city_gov': '',
                    'voivodeship_gov': 0,
                    'country_gov': None,
                    'email': '',
                    'phone': '',
                    'street': '',
                    'street_number': '',
                    'apt_number': '',
                    'zip_code': '',
                    'city': '',
                    'voivodeship': 0,
                    'country': None,
                    'curriculum_vitae': None,
                    'cv_filename': '',
                    'active_state': 'deleted',
                    'active': False,
                    })
