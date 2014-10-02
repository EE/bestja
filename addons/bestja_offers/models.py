# -*- coding: utf-8 -*-

from lxml import etree

from openerp import models, fields, api, exceptions


class Weekday(models.Model):
    _name = 'offers.weekday'
    name = fields.Char(size=3)
    full_name = fields.Char()


class Daypart(models.Model):
    _name = 'offers.daypart'
    name = fields.Char()


class Duration(models.Model):
    _name = 'offers.duration'
    select_kind = [
        ('periodic', 'okresowa'),
        ('cyclic', 'cykliczna'),
        ('flexible', 'elastyczna')
    ]
    select_interval = [
        (1, 'tydzień'),
        (2, '2 tygodnie'),
        (3, '3 tygodnie'),
        (4, '4 tygodnie'),
    ]

    offer = fields.Many2one('hr.job', string="Oferta", required=True)
    date_start = fields.Date(required=True, string="dnia")
    date_end = fields.Date(string="do dnia")
    kind = fields.Selection(select_kind, required=True, string="rodzaj akcji")
    interval = fields.Selection(select_interval, string="powtarzaj co")
    daypart = fields.Many2many('offers.daypart', string="pora dnia")
    hours = fields.Integer(string="liczba h")
    weekday = fields.Many2many('offers.weekday', string="powtarzaj w")

    @api.onchange('kind')
    def _onchange_kind(self):
        """
        Clear fields that are irrelevant to the new kind.
        """
        if self.kind not in ('periodic', 'cyclic'):
            self.weekday = None
            self.hours = 0
        if self.kind != 'cyclic':
            self.interval = None
            self.daypart = None

    @api.one
    @api.constrains('date_start', 'date_end')
    def _check_date_range(self):
        if not self.date_end:
            return

        if self.date_end < self.date_start:
            raise exceptions.ValidationError(
                "Data końcowa terminu akcji musi być późniejsza od jego daty początkowej!"
            )


class HelpeeGroup(models.Model):
    """Odbiorca pomocy"""
    _name = 'offers.helpee_group'
    name = fields.Char()


class Offer(models.Model):
    _inherit = 'hr.job'
    SELECT_STATES = [
        ('open', 'nieopublikowana'),
        ('recruit', 'opublikowana'),
        ('template', 'szablon')
    ]

    @api.model
    def _default_target_group(self):
        """All selected by default"""
        return self.env['volunteer.occupation'].search([])

    @api.model
    def _default_helpee_group(self):
        return self.env['offers.helpee_group'].search([])

    state = fields.Selection(SELECT_STATES)
    vacancies = fields.Integer(string="Liczba wakatów", default=1)
    project = fields.Many2one('project.project', string="Projekt", required=True)
    skills = fields.Many2many('volunteer.skill')
    wishes = fields.Many2many('volunteer.wish')
    drivers_license = fields.Many2one('volunteer.drivers_license', string="Prawa jazdy")
    sanepid = fields.Boolean(string="Badania sanepidu")
    forklift = fields.Boolean(string="Uprawnienia na wózek widłowy")
    latitude = fields.Float(string="Szerokość geograficzna")
    longitude = fields.Float(string="Długość geograficzna")
    target_group = fields.Many2many(
        'volunteer.occupation',
        default=_default_target_group,
        string="Kto jest adresatem oferty?",
        help="Wybierz grupę docelową np. studenci, emeryci."
    )
    helpee_group = fields.Many2many(
        'offers.helpee_group',
        default=_default_helpee_group,
        string="Komu wolontariusz może pomóc?",
        help="Wybierz grupę osób, z którymi będzie pracował."
    )
    desc_aim = fields.Text(
        string="Co jest celem oferty?",
        help="""Opisz w skrócie czym będzie zajmował się wolontariusz. np. Akcja będzie polegała na uporządkowaniu trawnika"""
    )
    desc_expectations = fields.Text(
        string="Co będzie robił wolontariusz?",
        help="Jakie będą oczekiwania wobec wolontariusza. \
        Co będzie musiał robić? np. Twoim zadaniem będzie grabienie liści, sadzenie trawy i krzewów"""
    )
    desc_why = fields.Text(
        string="Jak praca wolontariusza przyczyni się do zmiany?",
        help="Opisz dlaczego wolontariusz miałby się zaangażować w tą akcję, jaki problem pomoże rozwiązać, komu pomoże. \
        np. Domy starców nie mają funduszy na rewitalizację zieleni, a starsze osoby często przebywają w ogrodzie. \
        Twoja pomoc pozwoli seniorom miło spędzić czas w ogrodzie."
    )
    desc_benefits = fields.Text(
        string="Jakie korzyści będzie miał wolontariusz?"
    )
    desc_tools = fields.Text(
        string="Co zapewnia Twoja organizacja?"
    )
    desc_comments = fields.Text(
        string="Uwagi"
    )
    durations = fields.One2many('offers.duration', 'offer', string="Termin akcji", ondelete='restrict')
    image = fields.Binary("Photo")
    no_of_applications = fields.Integer(compute='_compute_no_of_applications')

    _sql_constraints = [
        ('name_company_uniq', 'CHECK(1=1)', ''),  # Overwrite and remove unique name constraint
    ]

    def __init__(self, pool, cr):
        """
        Set the new states again, for them to be fully recognized.
        """
        super(Offer, self).__init__(pool, cr)
        self._columns['state'].selection = self.SELECT_STATES

    @api.one
    @api.constrains('skills')
    def _check_skills_no(self):
        max_skills = self.env.user.company_id.bestja_max_skills
        if len(self.skills) > max_skills:
            raise exceptions.ValidationError("Wybierz maksymalnie {} umiejętności!".format(max_skills))

    @api.one
    @api.constrains('wishes')
    def _check_wishes_no(self):
        max_wishes = self.env.user.company_id.bestja_max_wishes
        if len(self.wishes) > max_wishes:
            raise exceptions.ValidationError("Wybierz maksymalnie {} obszarów działania!".format(max_wishes))

    @api.one
    @api.constrains('vacancies')
    def _check_vacancies(self):
        if self.vacancies <= 0:
            raise exceptions.ValidationError("Liczba wakatów powinna być większa od 0!")

    @api.one
    @api.depends('application_ids')
    def _compute_no_of_applications(self):
        self.no_of_applications = len(self.application_ids)

    @api.one
    def set_template(self):
        self.state = 'template'

    @api.multi
    def duplicate_template(self):
        for offer in self:
            default = {
                'name': offer.name,
                'status': 'open'
            }
            copy = offer.copy(default=default)

        # Redirect to the new object (edit form)
        view_id = self.env.ref('bestja_offers.bestja_offer_form').id
        return {
            'name': 'Oferty',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'hr.job',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
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
        company = self.env.user.company_id

        span_skills = doc.xpath("//span[@id='max_skills']")
        span_wishes = doc.xpath("//span[@id='max_wishes']")
        if span_skills:
            span_skills[0].text = str(company.bestja_max_skills)
        if span_wishes:
            span_wishes[0].text = str(company.bestja_max_wishes)

        view['arch'] = etree.tostring(doc)
        return view
