# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProjectMessage(models.TransientModel):
    _name = 'bestja.project.message_wizard'
    RECIPIENTS_CHOICES = [
        ('members', "Zespół projektu"),
    ]

    project = fields.Many2one(
        'bestja.project',
        string="Projekt",
        default=lambda self: self.env.context['active_id'],
    )
    content = fields.Text(string="Treść")
    recipients = fields.Selection(RECIPIENTS_CHOICES, default='members', string="Odbiorcy")

    @api.one
    def send_button(self):
        if self.recipients == 'members':
            self.send(recipients=self.project.members)

    @api.one
    def send(self, recipients):
        # Check permissions
        self.project.check_access_rights('write')
        self.project.check_access_rule('write')

        for member in recipients:
            self.project.with_context(message=self.content).send(
                template='bestja_project.msg_project_message',
                recipients=recipients,
                sender=self.env.user,
            )
