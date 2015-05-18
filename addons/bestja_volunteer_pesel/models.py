# -*- coding: utf-8 -*-
from operator import mul
from openerp import models, fields, api, exceptions


class Volunteer(models.Model):
    _inherit = 'res.users'

    pesel = fields.Char(string=u"PESEL")

    def __init__(self, pool, cr):
        super(Volunteer, self).__init__(pool, cr)
        self._add_permitted_fields(level='owner', fields={'pesel'})

    @api.one
    @api.constrains('pesel')
    def _check_pesel(self):
        if not self.pesel:
            return

        try:
            digits = map(int, self.pesel)
        except ValueError:
            raise exceptions.ValidationError("Numer PESEL może składać się wyłącznie z cyfr!")

        weights = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
        control_sum = -(sum(map(mul, digits[:-1], weights))) % 10
        if len(digits) != 11 or control_sum != digits[-1]:
            raise exceptions.ValidationError("Niepoprawny numer PESEL.")
