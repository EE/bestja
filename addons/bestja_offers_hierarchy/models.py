# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Offer(models.Model):
    _inherit = 'offer'

    top_project = fields.Many2one(
        string=u"Projekt główny",
        related='project.top_parent',
        store=True,
    )
    stored_application_count = fields.Integer(
        compute='_stored_application_count',
        compute_sudo=True,
        store=True,
        string="Aplikacje",
    )
    stored_accepted_application_count = fields.Integer(
        compute='_stored_application_count',
        compute_sudo=True,
        store=True,
        string="Zaakceptowane aplikacje",
    )
    one = fields.Integer(
        compute='_compute_one',
        store=True,
        string="Ofert",
    )

    @api.one
    @api.depends('applications', 'applications.state')
    def _stored_application_count(self):
        """
        A stored version used by the graph view
        """
        self.stored_application_count = len(self.applications)

        self.stored_accepted_application_count = len(
            self.applications.search([
                ('offer', '=', self.id),
                ('state', '=', 'accepted')
            ])
        )

    @api.one
    @api.depends('name')
    def _compute_one(self):
        """
        An ugly hack :( to get graph view to count offers
        """
        self.one = 1
