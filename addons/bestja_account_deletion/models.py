# -*- coding: utf-8 -*-

from openerp import models, fields, api
import uuid


class Volunteer(models.Model):
    _inherit = 'res.users'

    REASONS = [
        ('no_time', 'Nie mam czasu.'),
        ('location_change', 'Zmieniam miejsce zamieszkania.'),
        ('personal_change', 'Zmienia się moja sytuacja osobista (np. kończę studia).'),
        ('bad_offers', 'Oferty nie spełniły moich oczekiwań.'),
        ('no_satisfaction', 'Wolontariat nie sprawia mi już satysfakcji.'),
        ('else', 'Inny (wpisz powód)'),
    ]
    active_state = fields.Selection(selection_add=[('deleted', 'usunięty')])
    reason_for_deleting_account = fields.Selection(REASONS, string="Dlaczego chcesz usunąć konto?", required=True)
    reason_other_description = fields.Text()

    @api.one
    def delete_account(self):
        self.write({'login': uuid.uuid1(),
                    'name': 'Konto usunięte',
                    'street_gov': '',
                    'street_number_gov': '',
                    'apt_number_gov': '',
                    'zip_code_gov': '',
                    'email': '',
                    'phone': '',
                    'street': '',
                    'street_number': '',
                    'apt_number': '',
                    'zip_code': '',
                    'curriculum_vitae': None,
                    'cv_filename': '',
                    'active_state': 'deleted',
                    'active': False,
                    'pesel' : '',
                    'document_id_kind' : None,
                    'document_id' : '',
                    })
