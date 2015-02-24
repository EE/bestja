# -*- coding: utf-8 -*-

from openerp import models, fields


class CollagePhoto(models.Model):
    _name = 'collage_photo'

    name = fields.Char(string="Nazwa", required=True)
    reverse = fields.Text(string="Tekst na rewersie")
    attachment = fields.Binary(required=True, string="Plik")
    filename = fields.Char()
