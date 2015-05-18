# -*- coding: utf-8 -*-
import logging

from openerp import models, fields

_logger = logging.getLogger(__name__)


class OfferCategory(models.Model):
    _name = 'bestja.offer_category'

    name = fields.Char(string=u"nazwa", required=True)
    slug = fields.Char(string=u"identyfikator", required=True, index=True)

    _sql_constraints = [
        ('uffer_category_slug_uniq', 'unique("slug")', 'Identyfikator kategorii musi być unikalny!')
    ]


class Offer(models.Model):
    _inherit = 'offer'

    categories = fields.Many2many('bestja.offer_category', required=True, string=u"kategorie")
