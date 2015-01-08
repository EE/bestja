# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Wizard(models.TransientModel):
    _name = 'bestja.delete_account_wizard'

    def _default_users(self):
        return self.env['res.users'].browse(self.env.context.get('active_ids'))

    users = fields.Many2many(
        'res.users',
        string="Użytkownicy",
        required=True,
        default=_default_users,
    )

    @api.one
    def delete_account(self):
        self.users.delete_account()
