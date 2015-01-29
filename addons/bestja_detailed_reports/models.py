# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
from dateutil import parser


class Project(models.Model):
    _inherit = 'bestja.project'

    detailed_reports = fields.One2many('bestja.detailed_report', inverse_name='project')
    use_detailed_reports = fields.Boolean(required=True, string="Raporty szacunkowe do zbiórki żywności", default=True)


class CommodityGroup (models.Model):
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
    interested_organization = fields.Many2one(
        'organization',
        string="Zainteresowana organizacja",
        store=True,  # Needed by graph view
        related='detailed_report.interested_organization',
    )
    organization = fields.Many2one(
        'organization',
        string="Organizacja",
        store=True,
        related='detailed_report.project.organization',
    )

    _sql_constraints = [
        ('report_entries_uniq',
        'unique("detailed_report", "commodity")',
        "Dany element można wybrać tylko raz!")
    ]


class DetailedReport(models.Model):
    _name = 'bestja.detailed_report'
    _inherit = [
        'protected_fields.mixin',
        'ir.needaction_mixin',
        'message_template.mixin',
    ]
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
            ('parent.use_detailed_reports', '=', True),
            ('detailed_reports', '=', False),
            '|',
            ('manager', '=', self.env.user.id),
            ('organization.coordinator', '=', self.env.user.id)],
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
    interested_organization = fields.Many2one(
        'organization',
        string="Zainteresowane organizacje",
        compute="compute_interested_organization",
        store=True,
    )
    user_can_moderate = fields.Boolean(compute="compute_user_can_moderate")

    @api.one
    @api.depends('parent_project', 'project')
    def compute_interested_organization(self):
        level = self.project.organization.level
        if level <= 1:
            self.interested_organization = self.project.organization.id
        else:
            self.interested_organization = self.parent_project.organization.id

    @api.one
    @api.depends('report_entries')
    def compute_report_tonnage(self):
        """
        For showing the sum of kg of products
        """
        self.tonnage = 0.0
        for q in self.report_entries:
            self.tonnage += q.tonnage

    @api.one
    @api.depends('parent_project')
    def compute_user_can_moderate(self):
        """
        Is current user authorized to moderate (accept/reject) the detailed_report?
        """
        self.user_can_moderate = (
            self.parent_project.manager.id == self.env.user.id or
            self.parent_project.organization.coordinator.id == self.env.user.id
        )

    @api.one
    @api.constrains('report_entries')
    def check_report_entries(self):
        listlen = len(self.report_entries)
        newlist = set((i.commodity_code, i.detailed_report) for i in self.report_entries)
        if (listlen > len(newlist)):
            raise exceptions.ValidationError("Produkt o danym kodzie może mieć co najwyżej jeden wpis!")

    @api.one
    @api.depends('project')
    def compute_project_dates(self):
        """
        For nice format in the list of all projects.
        """
        if self.project:
            tmp_date = parser.parse(self.project.date_start).strftime("%d-%m-%Y")
            tmp_date += " -- "
            tmp_date += parser.parse(self.project.date_stop).strftime("%d-%m-%Y")
            self.dates = tmp_date

    @api.multi
    def set_sent(self):
        if (self.project.organization.level <= 1):
            self.state = 'accepted'
        else:
            self.state = 'sent'
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
        codes = []
        for com in self.env['bestja.commodity_group'].search([
                ('code', 'not in', [c.commodity_code for c in self.report_entries])]):
            codes.append(com)
            report_id = self.id
            interested_organization_id = self.interested_organization.id 
            self.env['bestja.report_entry'].create({
                'commodity': com.id,
                'detailed_report': report_id,
                'tonnage': 0.0,
                'interested_organization': interested_organization_id,
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
