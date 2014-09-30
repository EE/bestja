# -*- coding: utf-8 -*-

from lxml import etree

from openerp import models, fields, api, exceptions


class Weekday(models.Model):
    _name = 'offers.weekday'
    name = fields.Char()


class Daypart(models.Model):
    _name = 'offers.daypart'
    name = fields.Char()


class Duration(models.Model):
    select_kind = [
        (1, 'okresowa'),
        (2, 'cykliczna'),
        (3, 'elastyczna')
    ]
    select_interval = [
        (1, 'tydzień'),
        (2, '2 tygodnie'),
        (3, '3 tygodnie'),
        (4, '4 tygodnie'),
    ]
    _name = 'offers.duration'

    offer = fields.Many2one('hr.job', string="Oferta", required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date()
    kind = fields.Selection(select_kind)
    daypart = fields.Many2many('offers.daypart')
    hours = fields.Integer()
    weekday = fields.Many2many('offers.weekday')


class TargetGroup(models.Model):
    """Odbiorca pomocy"""
    _name = 'offers.target_group'
    name = fields.Char()


class Offer(models.Model):
    _inherit = 'hr.job'
    select_states = [
        ('open', 'nieopublikowana'),
        ('recruit', 'opublikowana')
    ]

    state = fields.Selection(select_states)
    vacancies = fields.Integer(string="Liczba wakatów")
    project = fields.Many2one('project.project', string="Projekt", required=True)
    skills = fields.Many2many('volunteer.skill')
    wishes = fields.Many2many('volunteer.wish')
    drivers_license = fields.Many2one('volunteer.drivers_license', string="Prawa jazdy")
    sanepid = fields.Boolean(string="Badania sanepidu")
    forklift = fields.Boolean(string="Uprawnienia na wózek widłowy")
    target_group = fields.Many2many(
        'volunteer.occupation',
        string="Kto jest adresatem oferty?",
        help="Wybierz grupę docelową np. studenci, emeryci."
    )
    helpee_group = fields.Many2many(
        'offers.target_group',
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
    durations = fields.One2many('offers.duration', 'offer', string="Terminy akcji")

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
