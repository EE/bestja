# -*- coding: utf-8 -*-

from openerp import models, fields


class Organization(models.Model):
    _inherit = 'organization'

    store_address_different = fields.Boolean(default=False, string=u"Zaznacz jeśli adres magazynu jest inny")
    store_street = fields.Char(string=u"Ulica")
    store_street_number = fields.Char(string=u"Numer budynku")
    store_zip_code = fields.Char(size=6, string=u"Kod pocztowy")
    store_city = fields.Char(string=u"Miejscowość")
