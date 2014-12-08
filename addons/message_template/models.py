# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
from openerp.addons.email_template.email_template import mako_template_env


class MessageTemplate(models.Model):
    _name = 'message_template'

    subject = fields.Char()
    body = fields.Text()
    model = fields.Char()

    @api.one
    def send(self, recipients, sender=None, record=None):
        recipient_partners = []
        for recipient in recipients:
            recipient_partners.append(
                (4, recipient.partner_id.id)
            )

        subtype = False
        if not sender:
            sender = self.env.ref('message_template.user_messages')
            subtype = self.env.ref('message_template.subtype_system_message')

        # Enable resolution of ${variables} inside body
        body_template = mako_template_env.from_string(tools.ustr(self.body))
        body_rendered = body_template.render({'record': record})

        self.env['mail.message'].sudo().create({
            'type': 'comment',
            'author_id': sender.partner_id.id,
            'partner_ids': recipient_partners,
            'model': self.model,
            'res_id': record.id,
            'record_name': record.name if record else None,
            'subject': self.subject,
            'body': body_rendered,
            'template': self.id,
            'subtype_id': subtype.id
        })

    @api.multi
    def send_group(self, group, sender=None, record=None):
        """
        Send a message to all users in a group `group`.
        """
        group_obj = self.env.ref(group)
        self.send(group_obj.users, sender, record)


class MessageTemplateMixin(models.AbstractModel):
    """
    This mixin enables model's records to be used with Odoo
    messages and adds `send` and `send_group` methods
    to the model.
    """
    _name = 'message_template.mixin'

    @api.one
    def send(self, template, recipients, sender=None):
        return self.env.ref(template).send(
            recipients=recipients,
            sender=sender,
            record=self,
        )

    @api.one
    def send_group(self, template, group, sender=None):
        return self.env.ref(template).send_group(
            group=group,
            sender=sender,
            record=self,
        )

    @api.multi
    def message_get_suggested_recipients(self):
        """
        Used by the messages module (in JS code).
        No, we don't want to add additional recipients, Odoo.
        Thanks, but no thanks.
        """
        return []

    @api.model
    def message_redirect_action(self):
        """
        Used by the messages module (in JS code).
        Returns an action for displaying the related record.
        """
        return self.env['mail.thread'].message_redirect_action()


class MailMessage(models.Model):
    _inherit = 'mail.message'

    template = fields.Many2one('message_template')
