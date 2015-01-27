# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.addons.website.models.website import slugify


class Offer(models.Model):
    _inherit = 'organization'

    city_slug = fields.Char(compute='compute_city_slug', store=True, index=True)

    @api.one
    @api.depends('city')
    def compute_city_slug(self):
        self.city_slug = slugify(self.city)
