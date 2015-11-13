# -*- coding: utf-8 -*-

from openerp import models, fields, api, SUPERUSER_ID, exceptions
import uuid


class Volunteer(models.Model):
    _inherit = 'res.users'

    REASONS = [
        ('no_time', u'Nie mam czasu.'),
        ('location_change', u'Zmieniam miejsce zamieszkania.'),
        ('personal_change', u'Zmienia się moja sytuacja osobista (np. kończę studia).'),
        ('bad_offers', u'Oferty nie spełniły moich oczekiwań.'),
        ('no_satisfaction', u'Wolontariat nie sprawia mi już satysfakcji.'),
        ('else', u'Inny (wpisz powód)'),
    ]
    active_state = fields.Selection(selection_add=[('deleted', 'usunięty')])
    reason_for_deleting_account = fields.Selection(REASONS, string=u"Dlaczego chcesz usunąć konto?")
    reason_other_description = fields.Text()

    @api.multi
    def get_deletion_reason(self):
        self.ensure_one()
        return dict(Volunteer.REASONS).get(self.reason_for_deleting_account)

    @api.one
    def delete_account(self):
        if not (self.env.uid == SUPERUSER_ID or self.user_has_groups('bestja_base.instance_admin')):
            raise exceptions.AccessError("Nie masz uprawnień do usuwania użytkowników!")

        self.sudo().write({
            'login': uuid.uuid1(),
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
            'pesel': '',
            'document_id_kind': None,
            'document_id': '',
        })
