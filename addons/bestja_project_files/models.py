# -*- coding: utf-8 -*-

from openerp import models, fields, api


class File(models.Model):
    _inherit = 'bestja.file'

    project = fields.Many2one(
        'bestja.project',
        string=u"Projekt",
        domain='''[
            '|',
                ('organization.coordinator', '=', uid),
                ('manager', '=', uid),
        ]''',
    )
    organization = fields.Many2one(
        'organization',
        string=u"Organizacja",
        related='project.organization'
    )


class Project(models.Model):
    _inherit = 'bestja.project'

    files = fields.One2many('bestja.file', 'project', string=u"Pliki")
    file_count = fields.Integer(compute='_file_count', string=u"Liczba plików")

    @api.one
    @api.depends('files')
    def _file_count(self):
        self.file_count = len(self.files)
