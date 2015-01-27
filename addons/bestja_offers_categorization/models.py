# -*- coding: utf-8 -*-

from openerp import models, fields


class OfferCategory(models.Model):
    _name = 'bestja.offer_category'

    name = fields.Char(string="nazwa", required=True)
    slug = fields.Char(string="identyfikator", required=True, index=True)

    _sql_constraints = [
        ('uffer_category_slug_uniq', 'unique("slug")', 'Identyfikator kategorii musi być unikalny!')
    ]


class Offer(models.Model):
    _inherit = 'offer'

    category = fields.Many2one('bestja.offer_category', required=True, index=True, string="kategoria")
