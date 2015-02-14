# -*- coding: utf-8 -*-

from openerp import models


class Volunteer(models.Model):
    _name = 'res.users'
    _inherit = [
        'res.users',
        'message_template.mixin'
    ]

    def __init__(self, pool, cr):
        super(Volunteer, self).__init__(pool, cr)
        self._remove_permitted_fields(level='privileged', fields={
            'email', 'phone', 'birthdate', 'place_of_birth',
            'citizenship', 'street_gov', 'street_number_gov', 'apt_number_gov', 'zip_code_gov', 'city_gov',
            'voivodeship_gov', 'country_gov', 'different_addresses', 'street', 'street_number', 'apt_number',
            'zip_code', 'city', 'voivodeship', 'country', 'pesel', 'document_id_kind', 'document_id'
        })