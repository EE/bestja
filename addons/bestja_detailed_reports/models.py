# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Project(models.Model):
    _inherit = 'bestja.project'

    detailed_reports = fields.One2many('bestja.detailed_report', inverse_name='project')
    enable_detailed_reports = fields.Boolean(string="Raporty szczegółowe do zbiórki żywności")
    use_detailed_reports = fields.Boolean(
        compute='compute_use_detailed_reports',
        compute_sudo=True,
        search='search_use_detailed_reports',
    )

    @api.one
    @api.depends('enable_detailed_reports', 'parent.enable_detailed_reports', 'parent.parent.enable_detailed_reports')
    def compute_use_detailed_reports(self):
        self.use_detailed_reports = (
            self.enable_detailed_reports or
            self.parent.enable_detailed_reports or
            self.parent.parent.enable_detailed_reports
        )

    def search_use_detailed_reports(self, operator, value):
        return [
            '|',  # noqa
                ('enable_detailed_reports', operator, value),
            '|',
                ('parent.enable_detailed_reports', operator, value),
                ('parent.parent.enable_detailed_reports', operator, value),
        ]


class CommodityGroup(models.Model):
    _name = 'bestja.commodity_group'
    _order = 'code'
    code = fields.Char(string="Kod")
    name = fields.Char(string="Nazwa")


class ReportEntry(models.Model):
    _name = 'bestja.report_entry'
    _order = 'commodity'

    detailed_report = fields.Many2one('bestja.detailed_report', ondelete='cascade', required=True)
    commodity = fields.Many2one('bestja.commodity_group', string="Nazwa", required=True, ondelete='cascade')
    commodity_code = fields.Char(string='Kod', related="commodity.code")
    tonnage = fields.Float(required=True, string="tonaż (kg)")
    responsible_organization = fields.Many2one(
        'organization',
        string="Zainteresowana organizacja",
        store=True,  # Needed by graph view
        related='detailed_report.responsible_organization',
    )
    organization = fields.Many2one(
        'organization',
        string="Organizacja",
        store=True,
        related='detailed_report.project.organization',
    )

    _sql_constraints = [
        ('report_entries_uniq', 'unique("detailed_report", "commodity")', "Dany element można wybrać tylko raz!")
    ]


class DetailedReport(models.Model):
    _name = 'bestja.detailed_report'
    _inherit = [
        'protected_fields.mixin',
        'ir.needaction_mixin',
        'message_template.mixin',
    ]
    _protected_fields = ['state']
    _order = 'write_uid desc'
    STATES = [
        ('sent', "wysłany"),
        ('accepted', "zaakceptowany"),
        ('draft', "szkic"),
        ('rejected', "odrzucony"),
    ]

    project = fields.Many2one(
        'bestja.project',
        required=True,
        string="Projekt",
        domain=lambda self: [
            ('use_detailed_reports', '=', True),
            ('detailed_reports', '=', False),
            '|',  # noqa
                ('manager', '=', self.env.uid),
                ('organization.coordinator', '=', self.env.uid),
        ],
        ondelete='restrict',
    )
    organization = fields.Many2one(
        'organization',
        string="Organizacja",
        related='project.organization',
    )
    name = fields.Char(string="Nazwa projektu", related="project.name")
    dates = fields.Char(string="Termin", compute="compute_project_dates", store=True)
    state = fields.Selection(STATES, default='draft', string="Status:")
    report_entries = fields.One2many('bestja.report_entry', inverse_name='detailed_report', string="Produkt")
    tonnage = fields.Float(string="Tonaż (kg)", compute="compute_report_tonnage", store=True)
    parent_project = fields.Many2one(
        'bestja.project',
        string="Projekt nadrzędny",
        related='project.parent',
        store=True,
    )
    responsible_organization = fields.Many2one(
        'organization',
        string="Zainteresowane organizacje",
        compute="compute_responsible_organization",
        compute_sudo=True,
        store=True,
    )
    user_can_moderate = fields.Boolean(compute="compute_user_can_moderate")

    @api.one
    @api.depends('parent_project', 'project')
    def compute_responsible_organization(self):
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

    @api.one
    @api.depends('report_entries')
    def compute_report_tonnage(self):
        """
        For showing the sum of kg of products
        """
        self.tonnage = sum(entry.tonnage for entry in self.report_entries)

    @api.one
    @api.depends('parent_project')
    def compute_user_can_moderate(self):
        """
        Is current user authorized to moderate (accept/reject) the detailed_report?
        """
        uid = self.env.uid
        project = self.sudo().project
        moderate_own = project.organization.level == 1 and \
            (project.manager.id == uid or project.organization.coordinator.id == uid)

        self.user_can_moderate = (
            moderate_own or project.parent.manager.id == self.env.uid or
            project.parent.organization.coordinator.id == self.env.uid
        )

    @api.one
    @api.depends('project')
    def compute_project_dates(self):
        """
        For nice format in the list of all projects.
        """
        date_start = fields.Datetime.from_string(self.project.date_start).strftime("%d-%m-%Y")
        date_stop = fields.Datetime.from_string(self.project.date_stop).strftime("%d-%m-%Y")
        return "{} — {}".format(date_start, date_stop)

    @api.multi
    def set_sent(self):
        self.sudo().state = 'sent'
        self.send(
            template='bestja_detailed_reports.msg_detailed_report_sent',
            recipients=self.parent_project.responsible_user,
            record_name=self.organization.name,
        )

    @api.multi
    def set_accepted(self):
        self.state = 'accepted'

    @api.multi
    def set_rejected(self):
        self.state = 'rejected'
        self.send(
            template='bestja_detailed_reports.msg_detailed_reports_rejected',
            recipients=self.sudo().project.responsible_user,
            sender=self.env.user,
        )

    @api.multi
    def continue_action(self):
        """
        For the continue button.
        """
        pass

    @api.multi
    def add_all_commodity_groups(self):
        """
        Button which adds all commodity groups to the report
        """
        domain = [('code', 'not in', [c.commodity_code for c in self.report_entries])]
        for commodity in self.env['bestja.commodity_group'].search(domain):
            self.env['bestja.report_entry'].create({
                'commodity': commodity.id,
                'detailed_report': self.id,
                'tonnage': 0.0,
                'responsible_organization': self.responsible_organization.id,
            })

    @api.multi
    def _is_permitted(self):
        """
        Allow authorized users to modify protected fields
        """
        permitted = super(DetailedReport, self)._is_permitted()
        return permitted or self.user_can_moderate

    @api.model
    def _needaction_domain_get(self):
        """
        Show sent count in menu.
        """
        return [
            ('state', '=', 'sent'),
        ]
