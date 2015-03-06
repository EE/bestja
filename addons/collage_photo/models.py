# -*- coding: utf-8 -*-

from openerp import models, fields


class CollagePhoto(models.Model):
    _name = 'collage_photo'

    name = fields.Char(string=u"Nazwa", required=True)
    reverse = fields.Text(string=u"Tekst na rewersie")
    attachment = fields.Binary(required=True, string=u"Plik")
    filename = fields.Char()
