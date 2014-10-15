# -*- coding: utf-8 -*-
import re
from operator import mul

from openerp import models, fields, api, exceptions


class Organization(models.Model):
    _name = 'organization'
    _parent = 'parent'

    name = fields.Char(string="Nazwa", required=True)
    krs = fields.Char(string="KRS")
    regon = fields.Char(string="REGON")
    nip = fields.Char(string="NIP")
    street_address = fields.Char(string="Ulica", required=True)
    city_address = fields.Char(string="Miejscowość", required=True)
    street_number = fields.Char(string="Numer", required=True)
    postal_code = fields.Char(size=6, string="Kod pocztowy")
    email = fields.Char(string="E-mail", required=True)
    phone = fields.Char(size=10, string="Numer Telefonu")
    www = fields.Char(string="WWW")
    fbfanpage = fields.Char(string="Fanpage na FB")
    parent = fields.Many2one('organization')
    coordinator = fields.Many2one(
        'res.users', ondelete='restrict',
        string="Koordynator",
        default=lambda self: self.env.user,
        groups="bestja_base.bestja_instance_admin"
    )
    active = fields.Boolean(default=False)
    organization_description = fields.Text(string="Opis Organizacji")
    image = fields.Binary("Photo")

    @api.one
    @api.constrains('email')
    def _check_email(self):
        email = self.email
        if not re.match(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", email):
            raise exceptions.ValidationError("Adres e-mail jest niepoprawny.")

    def check_control_sum(self, dig, dig_len, weights):
        control = sum( map (mul, dig[0:dig_len], weights))
        control = control % 11
        if control == 10:
            control = 0
        return control == dig[dig_len]

    @api.one
    @api.constrains('nip')
    def _check_nip(self):
        if not self.nip:
            return
        nip = self.nip.replace('-','')
        new_nip = nip.replace(' ','')

        if (len(new_nip) != 10):
            raise exceptions.ValidationError("Niepoprawna długość numeru NIP.")

        if (not new_nip.isdigit()):
            raise exceptions.ValidationError("Numer NIP nie może zawierać liter.")

        dig = map(int, new_nip)
        weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
        if not self.check_control_sum(dig, 9, weights):
            raise exceptions.ValidationError("Niepoprawny NIP.")


    @api.one
    @api.constrains('regon')
    def _check_regon(self):
        if not self.regon:
            return
        regon = self.regon.replace('-','').replace(' ','')

        if not (len(regon) == 9 or len(regon) == 14):
            raise exceptions.ValidationError("Niepoprawna długość numeru REGON.")

        if (not regon.isdigit()):
            raise exceptions.ValidationError("REGON nie może zawierać liter.")

        dig = map(int, regon)
        if (len(regon) == 9):
            weights = (8, 9, 2, 3, 4, 5, 6, 7)
            if not self.check_control_sum(dig, 8, weights):
                raise exceptions.ValidationError("Niepoprawny REGON.")

        if (len(regon) == 14):
            weights = (2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8)
            if not self.check_control_sum(dig, 13, weights):
                raise exceptions.ValidationError("Niepoprawny REGON.")
