# -*- coding: utf-8 -*-
from openerp import models, fields, api


class InvitationWizard(models.TransientModel):
    _name = 'bestja.project.invitation_wizard'

    def available_organizations(self):
        project_id = self.env.context.get('active_id')
        domain = []
        if project_id:
            project = self.env['bestja.project'].browse([project_id])
            invitations = self.env['bestja.project.invitation'].search([
                ('project', '=', project_id),
            ])
            domain += [('parent', '=', project.organization.id)]
            if invitations:
                domain += [('invitations', 'not in', invitations.ids)]
        return domain

    @api.model
    def default_organizations(self):
        """
        All organizations chosen by default.
        """
        domain = self.available_organizations()
        return self.env['organization'].search(domain)

    project = fields.Many2one(
        'bestja.project',
        default=lambda self: self.env.context['active_id'],
        string="Projekt",
    )
    organizations = fields.Many2many(
        'organization',
        domain=available_organizations,
        default=default_organizations,
        string="Organizacje",
    )
    description = fields.Text(string="Opis")

    @api.one
    def invite(self):
        for organization in self.organizations:
            invite = self.env['bestja.project.invitation'].create({
                'project': self.project.id,
                'organization': organization.id,
                'description': self.description,
            })
            invite.send(
                template='bestja_project_hierarchy.msg_invitation',
                recipients=organization.coordinator,
            )


class HierarchicalProjectMessage(models.TransientModel):
    _inherit = 'bestja.project.message_wizard'

    recipients = fields.Selection(selection_add=[('child_managers', "Menadżerowie podprojektów")])

    @api.one
    def send_button(self):
        super(HierarchicalProjectMessage, self).send_button()
        if self.recipients == 'child_managers':
            recipients = [child.responsible_user for child in self.sudo().project.children]
            self.send(recipients=recipients)
