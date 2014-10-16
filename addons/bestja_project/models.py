# -*- coding: utf-8 -*-

from openerp import models, fields


class Project(models.Model):
    _inherit = "project.project"

    organization = fields.Many2one('organization', required=True, string="Organizacja")
