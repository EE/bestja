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
    nip = fields.Char(required=True, string="NIP")
    street_address = fields.Char(string="Ulica", required=True)
    city_address = fields.Char(string="Miejscowość", required=True)
    street_number = fields.Char(string="Numer", required=True)
    postal_code = fields.Char(size=6, required=True, string="Kod pocztowy")
    email = fields.Char(string="E-mail", required=True)
    phone = fields.Char(required="True", string="Numer Telefonu")
    phone_extension = fields.Char(size=10, string="Numer wewnętrzny")
    www = fields.Char(string="WWW")
    fbfanpage = fields.Char(string="Fanpage na FB")
    parent = fields.Many2one(
        'organization',
        string="Organizacja nadrzędna",
        domain=[('parent', '=', False)]  # only top-level organizations
    )
    children = fields.One2many('organization', inverse_name='parent', string="Organizacje podrzędne")
    volunteers = fields.Many2many('res.users', string="Wolontariusze")
    coordinator = fields.Many2one(
        'res.users', ondelete='restrict',
        string="Koordynator",
        default=lambda self: self.env.user,
        groups="bestja_base.bestja_instance_admin"
    )
    active = fields.Boolean(
        default=False,
        groups="bestja_base.bestja_instance_admin",
        string="Zaakceptowana"
    )
    organization_description = fields.Text(string="Opis Organizacji")
    image = fields.Binary("Photo")

    _sql_constraints = [
        ('coordinator_uniq', 'unique(coordinator)', 'Jedna osoba nie może koordynować wielu organizacji!')
    ]

    @api.one
    @api.constrains('email')
    def _check_email(self):
        email = self.email
        if not re.match(r"^[_a-z0-9-]+([.+][_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", email):
            raise exceptions.ValidationError("Adres e-mail jest niepoprawny.")

    @staticmethod
    def is_gov_id_valid(number, weights):
        """
        Check governmental identification number.
        `weights` is a list of weights for subsequent digits.
        """
        try:
            digits = map(int, number)
        except ValueError:
            return False  # only proper numbers!

        if len(digits) != len(weights) + 1:
            return False

        control_sum = sum(map(mul, digits[:-1], weights)) % 11
        control_sum = 0 if control_sum == 10 else control_sum
        return control_sum == digits[-1]

    def clean_field_value(self, field_name):
        """
        Removes redundant characters from numeric fields
        """
        USELESS_CHARS = '-. /'
        value = str(getattr(self, field_name))
        if any(char in value for char in USELESS_CHARS):
            value = value.translate(None, USELESS_CHARS)
            setattr(self, field_name, value)

    @api.one
    @api.constrains('nip')
    def _check_nip(self):
        weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
        self.clean_field_value('nip')
        if self.nip and not self.is_gov_id_valid(self.nip, weights):
            raise exceptions.ValidationError("Niepoprawny NIP.")

    @api.one
    @api.constrains('regon')
    def _check_regon(self):
        weights = (8, 9, 2, 3, 4, 5, 6, 7)
        self.clean_field_value('regon')
        if self.regon and len(self.regon) > 9:
            weights = (2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8)

        if self.regon and not self.is_gov_id_valid(self.regon, weights):
            raise exceptions.ValidationError("Niepoprawny REGON.")

    @api.one
    @api.constrains('krs')
    def _check_krs(self):
        self.clean_field_value('krs')
        if self.krs and (len(self.krs) != 10 or not self.krs.isdigit()):
            raise exceptions.ValidationError("Niepoprawny KRS.")
