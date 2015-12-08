# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Wizard(models.TransientModel):
    _name = 'bestja_requests.accept_or_reject_report_wizard'

    def _default_reports(self):
        return self.env['bestja_requests.request'].browse(self.env.context.get('active_ids'))

    reports = fields.Many2many(
        'bestja_requests.request',
        string=u"Raporty potrzeb",
        default=_default_reports,
        relation="request_report_wizard_rel",
    )

    user_can_moderate = fields.Boolean(
        string=u"Czy użytkownik może moderować wszystkie raporty?",
        compute='_compute_all_user_can_moderate',
    )

    @api.one
    def accept_request_reports(self):
        self.reports.set_accepted()

    @api.one
    def reject_request_reports(self):
        self.reports.set_rejected()

    @api.one
    @api.depends('reports')
    def _compute_all_user_can_moderate(self):
        self.user_can_moderate = all(report.user_can_moderate for report in self.reports)
