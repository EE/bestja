# -*- coding: utf-8 -*-

from lxml import etree
from datetime import date

from openerp import tools, models, fields, api, exceptions
from openerp.addons.website.models.website import slug

from ..search import OffersIndex


class Weekday(models.Model):
    _name = 'offers.weekday'
    name = fields.Char(size=3, required=True)
    full_name = fields.Char(required=True)


class HelpeeGroup(models.Model):
    """Odbiorca pomocy"""
    _name = 'offers.helpee_group'
    name = fields.Char(requred=True)


class Offer(models.Model):
    _name = 'offer'
    _inherit = ['message_template.mixin']
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

    @api.multi
    def compute_image_medium(self):
        self.image_medium = tools.image_resize_image_medium(self.image)

    @api.one
    def inverse_image_medium(self):
        self.image = tools.image_resize_image_big(self.image_medium)

    state = fields.Selection(STATES, default='unpublished', string="Stan")
    name = fields.Char(string="Nazwa")
    vacancies = fields.Integer(string="Liczba wakatów", requred=True, default=1)
    project = fields.Many2one(
        'bestja.project',
        string="Projekt",
        required=True,
        domain=lambda self: [
            '|',
            ('organization.id', '=', self.env.user.coordinated_org.id),
            ('manager.id', '=', self.env.user.id),
        ]
    )
    organization = fields.Many2one(
        'organization',
        string="Organizacja",
        related='project.organization'
    )
    skills = fields.Many2many('volunteer.skill', required=True)
    wishes = fields.Many2many('volunteer.wish', required=True)
    drivers_license = fields.Many2one('volunteer.drivers_license', string="Prawa jazdy")
    sanepid = fields.Boolean(string="Badania sanepidu")
    forklift = fields.Boolean(string="Uprawnienia na wózek widłowy")
    location_name = fields.Char(string="Nazwa miejsca")
    address = fields.Char(string="Ulica i numer domu")
    city = fields.Char(string="Miasto")
    latitude = fields.Float(string="Szerokość geograficzna", digits=(7, 4))
    longitude = fields.Float(string="Długość geograficzna", digits=(7, 4))
    district = fields.Char(string="Dzielnica")
    target_group = fields.Many2many(
        'volunteer.occupation',
        default=_default_target_group,
        required=True,
        string="Kto jest adresatem oferty?",
        help="Wybierz grupę docelową np. studenci, emeryci."
    )
    helpee_group = fields.Many2many(
        'offers.helpee_group',
        default=_default_helpee_group,
        required=True,
        string="Komu wolontariusz może pomóc?",
        help="Wybierz grupę osób, z którymi będzie pracował."
    )
    desc_aim = fields.Text(
        required=True,
        string="Co jest celem oferty?",
        help="Opisz w skrócie czym będzie zajmował się wolontariusz. \
        np. Akcja będzie polegała na uporządkowaniu trawnika"
    )
    desc_expectations = fields.Text(
        required=True,
        string="Co będzie robił wolontariusz?",
        help="Jakie będą oczekiwania wobec wolontariusza. \
        Co będzie musiał robić? np. Twoim zadaniem będzie grabienie liści, sadzenie trawy i krzewów"""
    )
    desc_why = fields.Text(
        string="Jak praca wolontariusza przyczyni się do zmiany?",
        help="Opisz dlaczego wolontariusz miałby się zaangażować w tę akcję, \
        jaki problem pomoże rozwiązać, komu pomoże. \
        np. Domy starców nie mają funduszy na rewitalizację zieleni, a starsze osoby często przebywają w ogrodzie. \
        Twoja pomoc pozwoli seniorom miło spędzić czas w ogrodzie."
    )
    desc_benefits = fields.Text(
        required=True,
        string="Korzyści"
    )
    desc_tools = fields.Text(
        string="Co zapewnia Twoja organizacja?"
    )
    desc_comments = fields.Text(
        string="Uwagi"
    )
    image = fields.Binary()
    image_medium = fields.Binary(compute='compute_image_medium', inverse='inverse_image_medium', store=True)
    date_end = fields.Date(string="Termin ważności")
    remaining_days = fields.Integer(string="Wygasa za", compute='_remaining_days')
    kind = fields.Selection(KIND_CHOICES, required=True, string="rodzaj akcji")
    interval = fields.Selection(INTERVAL_CHOICES, string="powtarzaj co")
    daypart = fields.Many2many('volunteer.daypart', string="pora dnia")
    hours = fields.Integer(string="liczba h")
    weekday = fields.Many2many('offers.weekday', string="dzień tygodnia")
    comments_time = fields.Text(string="Uwagi dotyczące terminu")
    applications = fields.One2many('offers.application', 'offer', string="Aplikacje")
    application_count = fields.Integer(compute='_application_count')
    accepted_application_count = fields.Integer(compute='_application_count')
    localization = fields.Selection(
        LOCALIZATION_CHOICES,
        required=True,
        string="rodzaj lokalizacji",
        default="assigned",
    )

    @api.one
    @api.constrains('skills')
    def _check_skills_no(self):
        max_skills = int(self.env['ir.config_parameter'].get_param('bestja_offers.max_skills'))
        if len(self.skills) > max_skills:
            raise exceptions.ValidationError("Wybierz maksymalnie {} umiejętności!".format(max_skills))

    @api.one
    @api.constrains('wishes')
    def _check_wishes_no(self):
        max_wishes = int(self.env['ir.config_parameter'].get_param('bestja_offers.max_wishes'))
        if len(self.wishes) > max_wishes:
            raise exceptions.ValidationError("Wybierz maksymalnie {} obszarów działania!".format(max_wishes))

    @api.one
    @api.constrains('vacancies')
    def _check_vacancies(self):
        if self.vacancies <= 0:
            raise exceptions.ValidationError("Liczba wakatów musi być większa od 0!")

    @api.one
    @api.constrains('kind', 'hours', 'weekday', 'daypart', 'interval')
    def _check_time(self):
        if not self.kind == 'flexible':
            if not self.hours:
                raise exceptions.ValidationError("Wypełnij pole liczby godzin!")
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

    @api.model
    def fields_view_get(self, **kwargs):
        """
        Add information about maximum number of skills and fields of interest
        that can be chosen. They will be displayed as part of a help text.
        """
        view = super(Offer, self).fields_view_get(**kwargs)
        if 'view_type' in kwargs and kwargs['view_type'] != 'form':
            return view

        doc = etree.XML(view['arch'])
        conf = self.env['ir.config_parameter']

        span_skills = doc.xpath("//span[@id='max_skills']")
        span_wishes = doc.xpath("//span[@id='max_wishes']")
        if span_skills:
            span_skills[0].text = conf.get_param('bestja_offers.max_skills')
        if span_wishes:
            span_wishes[0].text = conf.get_param('bestja_offers.max_wishes')

        view['arch'] = etree.tostring(doc)
        return view

    # Whoosh indexing section starts here
    @api.multi
    def whoosh_reindex(self):
        """
        Update/Add offers to the whoosh index.
        """
        # utility function for creating lists of names of objects
        # in a record set
        list_names = lambda rset: [r[1] for r in rset.name_get()]

        index = OffersIndex(dbname=self.env.cr.dbname)
        writer = index.get_writer()
        for offer in self.sudo():
            pk = unicode(offer.id)
            if offer.state == 'published':
                writer.update_document(
                    pk=pk,
                    slug=slug(self),
                    name=offer.name,
                    wishes=list_names(offer.wishes),
                    target_group=list_names(offer.target_group),
                    organization=self.organization.name,
                )
            else:
                # Should not be public. Flag as removed from index.
                # Even if it wasn't there - no harm, no foul.
                writer.delete_by_term('pk', pk)
        writer.commit()

    @api.model
    def create(self, vals):
        record = super(Offer, self).create(vals)
        record.whoosh_reindex()
        return record

    @api.multi
    def write(self, vals):
        val = super(Offer, self).write(vals)
        self.whoosh_reindex()
        return val

    @api.multi
    def unlink(self):
        val = super(Offer, self).unlink()
        index = OffersIndex(dbname=self.env.cr.dbname)
        writer = index.get_writer()
        for offer in self:
            writer.delete_by_term('pk', unicode(offer.id))
        writer.commit()
        return val

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
