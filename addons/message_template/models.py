# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
from openerp.addons.email_template.email_template import mako_template_env


class MessageTemplate(models.Model):
    _name = 'message_template'

    subject = fields.Char()
    body = fields.Text()
    model = fields.Char()

    @api.one
    def send(self, recipients, sender=None, record=None, record_name=None):
        recipient_partners = []
        for recipient in recipients:
            recipient_partners.append(
                (4, recipient.partner_id.id)
            )

        subtype = None
        if not sender:
            sender = self.env.ref('message_template.user_messages')
            subtype = self.env.ref('message_template.subtype_system_message')

        # Enable resolution of ${variables} inside body
        body_template = mako_template_env.from_string(tools.ustr(self.body))
        body_rendered = body_template.render({
            'record': record,
            'context': self.env.context,
        })

        self.env['mail.message'].sudo().create({
            'type': 'comment',
            'author_id': sender.partner_id.id,
            'partner_ids': recipient_partners,
            'model': self.model,
            'res_id': record and record.id,
            'record_name': record_name or (record and record.display_name),
            'subject': self.subject,
            'body': body_rendered,
            'template': self.id,
            'subtype_id': subtype and subtype.id
        })

    @api.multi
    def send_group(self, group, sender=None, record=None, record_name=None):
        """
        Send a message to all users in a group `group`.
        """
        group_obj = self.env.ref(group)
        self.send(
            recipients=group_obj.sudo().users,
            sender=sender,
            record=record,
            record_name=record_name,
        )


class MessageTemplateMixin(models.AbstractModel):
    """
    This mixin enables model's records to be used with Odoo
    messages and adds `send` and `send_group` methods
    to the model.
    """
    _name = 'message_template.mixin'

    @api.one
    def send(self, template, recipients, sender=None, record_name=None):
        return self.env.ref(template).send(
            recipients=recipients,
            sender=sender,
            record=self,
            record_name=record_name,
        )

    @api.one
    def send_group(self, template, group, sender=None, record_name=None):
        return self.env.ref(template).send_group(
            group=group,
            sender=sender,
            record=self,
            record_name=record_name,
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

    @api.multi
    def message_post(self, *args, **kwargs):
        """
        Used by the messages module to reply in a thread.
        """
        return self.env['mail.thread'].message_post(*args, **kwargs)

    @api.model
    def _get_access_link(self, mail, partner):
        """
        Used to generate a link to the associated object in e-mail notification.
        """
        return self.env['mail.thread']._get_access_link(mail, partner)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    template = fields.Many2one('message_template')
