# -*- coding: utf-8 -*-

from openerp import models, api


class Message(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _get_default_from(self):
        """
        All message notification should be send from the official
        company e-mail address.
        """
        company = self.env.user.company_id
        return (company.name, company.email)
