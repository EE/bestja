# -*- coding: utf-8 -*-
from openerp import models, fields, api


class RecipientsChoices(models.Model):
    _name = 'recipients.choices'

    name = fields.Char(
        required=True,
        string=u"Odbiorcy",
    )
    id_name = fields.Char(
        required=True,
    )


class ProjectMessage(models.TransientModel):
    _name = 'bestja.project.message_wizard'

    @api.model
    def default_recipients(self):
        return self.env.ref('bestja_project.members')

    project = fields.Many2one(
        'bestja.project',
        string=u"Projekt",
        required=True,
        default=lambda self: self.env.context['active_id'],
    )
    content = fields.Html(string=u"Treść", required=True)
    recipients = fields.Many2many(
        'recipients.choices',
        string=u"Odbiorcy",
        default=default_recipients,
    )
    subject = fields.Char(
        required=True,
        string=u"Temat",
    )

    @api.one
    def send_button(self):
        for recipient in self.recipients:
            if recipient.id_name == 'members':
                self.send(recipients=self.project.members)

    @api.one
    def send(self, recipients):
        # Check permissions
        self.project.check_access_rights('write')
        self.project.check_access_rule('write')

        for recipient in recipients:
            self.project.with_context(
                message=self.content,
                subject=self.subject,
            ).send(
                template='bestja_project.msg_project_message',
                recipients=recipient,
                sender=self.env.user,
            )
