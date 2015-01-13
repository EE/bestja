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


class ReportWizard(models.TransientModel):
    _name = 'bestja.report_account_deletion_wizard'

    reason = fields.Text(string="Dlaczego chcesz usunąć konto?", required=True)

    @api.one
    def report_delete_account(self):
        """
        When user wants to delete account, he reports this to admin.
        """
        self.env.user.reason_for_deleting_account = self.reason
        self.env.user.send_group(
            template='bestja_account_deletion.msg_report_account_deletion_to_admin',
            group='bestja_base.instance_admin',
            sender=self.env.user,
        )
