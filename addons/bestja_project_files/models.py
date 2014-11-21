# -*- coding: utf-8 -*-

from openerp import models, fields, api


class File(models.Model):
    _inherit = 'bestja.file'

    project = fields.Many2one('bestja.project', string="Projekt")
    organization = fields.Many2one(
        'organization',
        compute='_compute_organization',
        string="Organizacja"
    )

    @api.one
    @api.depends('project')
    def _compute_organization(self):
        self.organization = self.project.organization


class Project(models.Model):
    _inherit = 'bestja.project'

    files = fields.One2many('bestja.file', 'project', string="Pliki")
    file_count = fields.Integer(compute='_file_count', string="Liczba plików")

    @api.one
    @api.depends('files')
    def _file_count(self):
        self.file_count = len(self.files)
