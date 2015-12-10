# -*- coding: utf-8 -*-
from StringIO import StringIO
import csv
import locale
from collections import defaultdict

from openerp import models, fields, api, exceptions


class Wizard(models.TransientModel):
    _name = 'bestja.accept_or_reject_report_wizard'

    def _default_reports(self):
        return self.env['bestja.detailed_report'].browse(self.env.context.get('active_ids'))

    reports = fields.Many2many(
        'bestja.detailed_report',
        string=u"Raporty szczegółowe",
        default=_default_reports,
        relation="detailed_report_wizard_rel",
    )

    user_can_moderate = fields.Boolean(
        string=u"Czy użytkownik może moderować wszystkie raporty?",
        compute='_compute_all_user_can_moderate',
    )

    @api.one
    def accept_detailed_reports(self):
        self.reports.set_accepted()

    @api.one
    def reject_detailed_reports(self):
        self.reports.set_rejected()

    @api.one
    @api.depends('reports')
    def _compute_all_user_can_moderate(self):
        self.user_can_moderate = all(report.user_can_moderate for report in self.reports)


class SetSentWizard(models.TransientModel):
    _name = 'bestja.set_sent_report_wizard'

    def _default_reports(self):
        return self.env['bestja.detailed_report'].browse(self.env.context.get('active_ids'))

    detailed_report = fields.Many2one(
        'bestja.detailed_report',
        default=_default_reports,
        string=u"Raport:",
    )

    @api.one
    def set_detailed_report_sent(self):
        self.detailed_report.set_sent()


class ImportWizard(models.TransientModel):
    _name = 'bestja_detailed_reports.import_wizard'

    def _default_reports(self):
        return self.env['bestja.detailed_report'].browse(self.env.context.get('active_ids'))

    detailed_report = fields.Many2one(
        'bestja.detailed_report',
        default=_default_reports,
        string=u"Raport",
    )
    import_file = fields.Binary(required=True, string=u"Plik CSV")

    @api.multi
    def start_import(self):
        csv_content = self.import_file.decode('base64')
        dialect = csv.Sniffer().sniff(csv_content, delimiters=[';'])  # Try to guess the format
        rows = csv.reader(StringIO(csv_content), dialect)

        groups = defaultdict(float)

        for line_no, row in enumerate(rows, start=1):
            try:
                row = [unicode(cell, 'utf-8') for cell in row]
            except UnicodeDecodeError:
                raise exceptions.ValidationError(
                    """Problem z kodowaniem znaku w linii {}.
                    Upewnij się, że plik CSV używa kodowania UTF-8""".format(line_no)
                )
            if len(row) < 2:
                continue

            code = row[0].strip().split('_')[0]
            try:
                tonnage = float(row[1].replace(',', '.'))
            except:
                raise exceptions.ValidationError(
                    "Problem w linii {}. Upewnij się, że podana liczba jest poprawna".format(line_no)
                )
            groups[code] += tonnage

        for code, tonnage in groups.iteritems():
            commodity_group = self.env['bestja.commodity_group'].search([('code', '=', code)])
            if not commodity_group:
                raise exceptions.ValidationError(
                    """Nie znaleziono grupy produktów z kodem \"{}\".
                    Upewnij się, że kody podane w pliku CSV są poprawne""".format(code)
                )

            existing_entry = self.env['bestja.report_entry'].search([
                ('detailed_report', '=', self.detailed_report.id),
                ('commodity', '=', commodity_group.id),
            ])
            if existing_entry:
                existing_entry.tonnage = tonnage
            else:
                self.env['bestja.report_entry'].create({
                    'detailed_report': self.detailed_report.id,
                    'commodity': commodity_group.id,
                    'tonnage': tonnage,
                })
