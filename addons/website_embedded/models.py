# -*- coding: utf-8 -*-

from openerp import models, fields


class EmbeddedObject(models.Model):
    _name = 'embedded_object'

    KINDS = [
        ('elearning', "e-learning"),
        ('biuletyn', "biuletyn wolontariuszy"),
    ]

    name = fields.Char(string=u"Nazwa", required=True)
    kind = fields.Selection(
        KINDS,
        required=True,
        string=u"Typ",
    )
    embed_code = fields.Text(string="Kod osadzenia", required=True)
    thumbnail_url = fields.Char(string=u"Adres miniaturki", required=True)
    description = fields.Html(string=u"Opis")
