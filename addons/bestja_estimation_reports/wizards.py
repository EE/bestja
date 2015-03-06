# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AddToSummaryWizard(models.TransientModel):
    _name = 'bestja.add_to_summary_wizard'

    def _default_reports(self):
        """
        Reports chosen by default.
        """
        return self.env['bestja.estimation_report'].browse(self.env.context.get('active_ids'))

    estimation_report = fields.Many2one(
        'bestja.estimation_report',
        default=_default_reports,
        string=u"Raport:",
    )

    @api.one
    def add_estimation_reports_to_summary(self):
        self.estimation_report.add_to_summary()
