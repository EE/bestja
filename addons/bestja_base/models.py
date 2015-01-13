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
        return u'{} <{}>'.format(company.name, company.email)


class StopSpying(models.Model):
    _inherit = 'publisher_warranty.contract'

    @api.multi
    def update_notification(*args, **kwargs):
        # This method is used by Odoo to phone home to OpenERP S.A.
        # No more.
        return True


class Website(models.Model):
    _inherit = 'website'

    @api.one
    def set_language(self, lang_code):
        """
        Set language for a website.
        If the language is not already loaded
        (for example using `--load-language` option)
        it will be ignored.
        """
        # TODO:
        # I expect we will have a separate "bestja_website" module
        # in the future. This code should be moved there.
        lang = self.env['res.lang'].search([('code', '=', lang_code)])
        if lang:
            self.write({
                'language_ids': [(6, 0, [lang.id])],
                'default_lang_id': lang.id,
            })
