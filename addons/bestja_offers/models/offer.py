# -*- coding: utf-8 -*-
from datetime import date

from openerp import models, fields, api, exceptions
from openerp.addons.website.models.website import slug


class Weekday(models.Model):
    _name = 'offers.weekday'
    name = fields.Char(size=3, required=True)
    full_name = fields.Char(required=True)


class Offer(models.Model):
    _name = 'offer'
    _inherit = ['message_template.mixin']
    _order = 'id desc'
    STATES = [
        ('unpublished', "nieopublikowana"),
        ('published', "opublikowana"),
        ('archive', "archiwalna"),
        ('template', "szablon"),
    ]
    KIND_CHOICES = [
        ('periodic', 'okresowa'),
        ('cyclic', 'cykliczna'),
        ('flexible', 'elastyczna')
    ]
    LOCALIZATION_CHOICES = [
        ('assigned', 'Oferta ma przypisaną lokalizację.'),
        ('no_localization', 'Oferta nie ma przypisanej lokalizacji, np. kierowca.'),
        ('remote', 'To jest praca zdalna, np. grafik.')
    ]
    INTERVAL_CHOICES = [
        (1, 'tydzień'),
        (2, '2 tygodnie'),
        (3, '3 tygodnie'),
        (4, '4 tygodnie'),
    ]

    @api.model
    def _default_target_group(self):
        """All selected by default"""
        return self.env['volunteer.occupation'].search([])

    @api.model
    def _default_helpee_group(self):
        return self.env['offers.helpee_group'].search([])

    state = fields.Selection(STATES, default='unpublished', string=u"Stan")
    name = fields.Char(required=True, string=u"Nazwa")
    unlisted = fields.Boolean(default=False, string="Oferta ukryta")
    vacancies = fields.Integer(string=u"Liczba wakatów", required=True, default=1)
    project = fields.Many2one(
        'bestja.project',
        string=u"Projekt",
        required=True,
        domain=lambda self: [
            '|',
            ('organization.id', '=', self.env.user.coordinated_org.id),
            ('manager.id', '=', self.env.uid),
        ]
    )
    organization = fields.Many2one(
        'organization',
        string=u"Organizacja",
        related='project.organization'
    )
    organization_image = fields.Binary(related='organization.image')
    skills = fields.Many2many('volunteer.skill', required=True)
    wishes = fields.Many2many('volunteer.wish', required=True)
    location_name = fields.Char(string=u"Nazwa miejsca")
    address = fields.Char(string=u"Ulica i numer domu")
    city = fields.Char(string=u"Miasto")
    latitude = fields.Float(string=u"Szerokość geograficzna", digits=(7, 4))
    longitude = fields.Float(string=u"Długość geograficzna", digits=(7, 4))
    district = fields.Char(string=u"Dzielnica")
    description = fields.Text(required=True, string=u"Na czym będzie polegała Twoja praca")
    expectations = fields.Text(required=True, string=u"Czego oczekujemy")
    benefits = fields.Text(required=True, string=u"Co oferujemy")
    tools = fields.Text(string=u"Co zapewniamy")
    comments = fields.Text(string=u"Uwagi")
    date_end = fields.Date(string=u"Termin ważności")
    remaining_days = fields.Integer(string=u"Wygasa za", compute='_remaining_days')
    kind = fields.Selection(KIND_CHOICES, required=True, string=u"rodzaj akcji")
    interval = fields.Selection(INTERVAL_CHOICES, string=u"powtarzaj co")
    daypart = fields.Many2many('volunteer.daypart', string=u"pora dnia")
    hours = fields.Integer(string=u"liczba h/tyg.")
    weekday = fields.Many2many('offers.weekday', string=u"dzień tygodnia")
    comments_time = fields.Text(string=u"Uwagi dotyczące terminu")
    applications = fields.One2many('offers.application', 'offer', string=u"Aplikacje")
    application_count = fields.Integer(compute='_application_count')
    accepted_application_count = fields.Integer(compute='_application_count')
    localization = fields.Selection(
        LOCALIZATION_CHOICES,
        required=True,
        string=u"rodzaj lokalizacji",
        default="assigned",
    )

    @api.one
    @api.constrains('vacancies')
    def _check_vacancies(self):
        if self.vacancies <= 0:
            raise exceptions.ValidationError("Liczba wakatów musi być większa od 0!")

    @api.one
    @api.constrains('kind', 'weekday', 'daypart', 'interval')
    def _check_time(self):
        if not self.kind == 'flexible':
            if not self.weekday:
                raise exceptions.ValidationError("Wypełnij pole dnia tygodnia!")
            if not self.daypart:
                raise exceptions.ValidationError("Wypełnij pole pory dnia!")
            if self.kind == 'cyclic' and not self.interval:
                raise exceptions.ValidationError("Wypełnij pole \"powtarzaj w\"!")

    @api.one
    @api.constrains('location_name', 'address', 'city', 'latitude', 'longitude')
    def _check_location(self):
        if self.localization != 'assigned':
            return

        if not self.location_name:
            raise exceptions.ValidationError("Wypełnij pole nazwy miejsca!")
        if not self.address:
            raise exceptions.ValidationError("Wypełnij pole adresu!")
        if not self.city:
            raise exceptions.ValidationError("Wypełnij pole miasta!")
        if not self.latitude or not self.longitude:
            raise exceptions.ValidationError("Wskaż położenie na mapie!")

    @api.onchange('kind')
    def _onchange_kind(self):
        """
        Clear fields that are irrelevant to the new kind.
        """
        if self.kind not in ('periodic', 'cyclic'):
            self.weekday = None
            self.hours = 0
            self.daypart = None
        if self.kind != 'cyclic':
            self.interval = None

    @api.onchange('localization')
    def _onchange_localization(self):
        """
        Clear fields that are irrelevant with no localization.
        """
        if self.localization != 'assigned':
            self.location_name = False
            self.address = False
            self.city = False
            self.district = False

    @api.one
    @api.depends('applications', 'applications.state')
    def _application_count(self):
        self.application_count = len(
            self.applications.search([
                ('offer', '=', self.id),
                ('state', '!=', 'rejected')
            ])
        )
        self.accepted_application_count = len(
            self.applications.search([
                ('offer', '=', self.id),
                ('state', '=', 'accepted')
            ])
        )

    @api.one
    @api.depends('date_end')
    def _remaining_days(self):
        if self.date_end is False:
            self.remaining_days = False
        else:
            last_day = fields.Date.from_string(self.date_end)
            self.remaining_days = (last_day - date.today()).days

    @api.one
    def set_template(self):
        self.state = 'template'

    @api.one
    def set_published(self):
        self.state = 'published'

    @api.one
    def set_unpublished(self):
        self.state = 'unpublished'

    @api.multi
    def duplicate_template(self):
        for offer in self:
            default = {
                'name': offer.name,
                'state': 'unpublished'
            }
            copy = offer.copy(default=default)

        return {
            'view_mode': 'form',
            'res_model': 'offer',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'res_id': copy.id,
        }

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        """
        Every time an offer is read check if it didn't expire.
        """
        if fields:
            fields.extend(['remaining_days', 'state'])
        vals = super(Offer, self).read(fields=fields, load=load)
        for rec in vals:
            if rec['state'] in ('published', 'unpublished') and rec['remaining_days'] < 0:
                # Expired! Change the state.
                self.browse([rec['id']]).state = 'archive'
                rec['state'] = 'archive'
        return vals

    @api.multi
    def get_public_url(self):
        return '/offer/{}/'.format(slug(self))

    @api.multi
    def show_website_action(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.get_public_url(),
            'target': 'new',
        }
