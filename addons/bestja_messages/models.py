# -*- coding: utf-8 -*-
from urlparse import urljoin

from openerp import models, api, tools


class Notification(models.Model):
    _inherit = 'mail.notification'

    @api.model
    def get_signature_footer(self, user_id, res_model=None, res_id=None, user_signature=True):
        """
        Generate Footer in mail notifications.
        """
        footer = ""
        user = self.env['res.users'].browse([user_id])

        if user_signature:
            footer = tools.append_content_to_html(footer, u"<p>{}</p>".format(user.name), plaintext=False)

        website = user.company_id.website
        website_url = ('http://%s' % website) if not website.lower().startswith(('http:', 'https:')) else website

        signature = u"""<br/>-- <br/>
Wiadomość wysłana przez <a href='{url}'>{name}</a> poprzez aplikację (C) 2015 GooDoo.ee.""".format(
            url=website_url,
            name=user.company_id.name,
        )
        footer = tools.append_content_to_html(footer, signature, plaintext=False, container_tag='div')

        return footer


class Mail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def _get_partner_access_link(self, mail, partner=None):
        if partner and partner.user_ids and mail.model and mail.record_name:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')

            url = urljoin(base_url, self.env[mail.model]._get_access_link(mail, partner))
            return u"<br/>Zobacz szczegóły na temat: <a href='{url}'>{name}</a>".format(
                url=url,
                name=mail.record_name,
            )
        else:
            return None
