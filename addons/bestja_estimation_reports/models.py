# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


class Project(models.Model):
    _inherit = 'bestja.project'

    estimation_reports = fields.One2many('bestja.estimation_report', inverse_name='project')
    enable_estimation_reports = fields.Boolean(string=u"Raporty szacunkowe do zbiórki żywności")

    use_estimation_reports = fields.Boolean(
        compute='_compute_use_estimation_reports',
        compute_sudo=True,
        search='search_use_estimation_reports',
    )

    @api.one
    @api.depends(
        'enable_estimation_reports',
        'parent.enable_estimation_reports',
        'parent.parent.enable_estimation_reports'
    )
    def _compute_use_estimation_reports(self):
        self.use_estimation_reports = (
            self.enable_estimation_reports or
            self.parent.enable_estimation_reports or
            self.parent.parent.enable_estimation_reports
        )

    def search_use_estimation_reports(self, operator, value):
        return [
            '|',  # noqa
                ('enable_estimation_reports', operator, value),
            '|',
                ('parent.enable_estimation_reports', operator, value),
                ('parent.parent.enable_estimation_reports', operator, value),
        ]


class EstimationReportEntry(models.Model):
    _name = 'bestja.estimation_report_entry'

    estimation_report = fields.Many2one(
        'bestja.estimation_report',
        ondelete='cascade',
        required=True,
        string=u"raport szacunkowy",
    )
    day_in_store = fields.Many2one('bestja_stores.day', required=True, string=u"dzień")
    day = fields.Date(
        related='day_in_store.date',
        store=True,
    )
    tonnage = fields.Float(required=True, string=u"Liczba kg")
    store = fields.Many2one(
        related='day_in_store.store.store',
        store=True,
        string=u"sklep",
    )
    store_project = fields.Many2one(
        'bestja.project',
        required=True,
        related='estimation_report.project'
    )
    store_name = fields.Char(
        string=u"nazwa sklepu",
        related='day_in_store.store.store.display_name',
        store=True,
    )
    store_address = fields.Char(
        required=True,
        related='store.address',
    )
    store_city = fields.Char(required=True, related='store.city')
    chain = fields.Many2one(
        related='store.chain',
        store=True,
    )
    organization = fields.Many2one(
        'organization',
        string=u"organizacja",
        related='estimation_report.organization',
        store=True,
    )
    responsible_organization = fields.Many2one(
        'organization',
        string=u"organizacja odpowiedzialna",
        store=True,  # Needed by graph view
        related='estimation_report.responsible_organization',
    )
    responsible_project = fields.Many2one(
        'bestja.project',
        string=u"projekt odpowiedzialny",
        store=True,  # Needed by graph view
        related='estimation_report.responsible_project',
    )
    parent_project = fields.Many2one(
        'bestja.project',
        string=u"projekt nadrzędny",
        related='estimation_report.parent_project',
        store=True,
    )
    top_project = fields.Many2one(
        'bestja.project',
        string=u"projekt super nadrzędny",
        related='estimation_report.top_project',
        store=True,
    )


class EstimationReport(models.Model):
    _name = 'bestja.estimation_report'
    _inherit = [
        'protected_fields.mixin',
        'ir.needaction_mixin',
    ]
    _protected_fields = ['state']
    STATES = [
        ('sent', 'dodany do zestawienia'),
        ('draft', 'szkic'),
    ]
    project = fields.Many2one(
        'bestja.project',
        required=True,
        string=u"projekt",
        domain=lambda self: [
            ('use_estimation_reports', '=', True),
            '|',  # noqa
                ('manager', '=', self.env.uid),
                ('organization.coordinator', '=', self.env.uid),
        ],
        ondelete='restrict',
    )
    date = fields.Date(
        required=True,
        string=u"dzień",
    )
    name = fields.Char(string=u"nazwa projektu", related="project.name")
    report_entries = fields.One2many(
        'bestja.estimation_report_entry',
        inverse_name="estimation_report",
        string=u"sklep"
    )
    state = fields.Selection(STATES, default='draft', string=u"status")
    organization = fields.Many2one(
        'organization',
        string=u"organizacja",
        related='project.organization',
    )
    parent_project = fields.Many2one(
        'bestja.project',
        string=u"projekt nadrzędny",
        related='project.parent',
        store=True,
    )
    responsible_organization = fields.Many2one(
        'organization',
        string=u"organizacja odpowiedzialna",
        compute="_compute_responsible_organization",
        compute_sudo=True,
        store=True,
    )

    responsible_project = fields.Many2one(
        'bestja.project',
        string=u"projekt odpowiedzialny",
        compute='_compute_responsible_project',
        store=True,
    )
    top_project = fields.Many2one(
        'bestja.project',
        string=u"projekt super nadrzędny",
        related='project.top_parent',
        store=True,
    )
    total_tonnage = fields.Float(string=u"Suma", compute="_compute_report_tonnage", store=True)
    _sql_constraints = [(
        'estimation_report_unique',
        'unique("project", "date")',
        "Dla danego projektu i dnia może istnieć tylko jeden raport!"
    )]

    @api.one
    @api.depends('report_entries')
    def _compute_report_tonnage(self):
        """
        For showing the sum of kg of products
        """
        self.total_tonnage = sum(entry.tonnage for entry in self.report_entries)

    @api.one
    @api.depends('parent_project', 'project')
    def _compute_responsible_project(self):
        """
        For statistics for the middle level organization,
        allowing it to see the statistics of both its children and itself.
        """
        project = self.project
        level = project.organization.level
        if level <= 1:
            self.responsible_project = project.id
        else:
            self.responsible_project = project.parent.id

    @api.one
    @api.depends('parent_project', 'project')
    def _compute_responsible_organization(self):
        """
        The organizations on the middle level (1) are responsible for managing
        their reports and reports of their children.
        This field can be used to group all reports managed by
        a single organization together.
        """
        project = self.project
        level = project.organization.level
        if level <= 1:
            self.responsible_organization = project.organization.id
        else:
            self.responsible_organization = project.parent.organization.id

    @api.multi
    def continue_action(self):
        """
        For the continue button, adds all stores related to the project and day.
        """

    @api.model
    def create(self, vals):
        record = super(EstimationReport, self).create(vals)
        domain = [
            ('date', '=', record.date),
            ('store.project', '=', record.project.id),
            ('store.state', '=', 'activated')
        ]
        for day_in_store in record.env['bestja_stores.day'].search(domain):
            record.env['bestja.estimation_report_entry'].create({
                'estimation_report': record.id,
                'day_in_store': day_in_store.id,
                'tonnage': 0.0,
            })
        return record

    @api.one
    def add_to_summary(self):
        self.sudo().state = 'sent'

    @api.one
    @api.constrains('date', 'project')
    def _check_date_in_project(self):
        if not self.project.date_start <= self.date <= self.project.date_stop:
            raise exceptions.ValidationError("Wybrano dzień poza czasem trwania projektu!")
