# -*- coding: utf-8 -*-

from lxml import etree

from openerp import models, fields, api, exceptions

import search


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

    offer = fields.Many2one('offer', string="Oferta", required=True)
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
    _name = 'offer'
    SELECT_STATES = [
        ('unpublished', 'nieopublikowana'),
        ('published', 'opublikowana'),
        ('template', 'szablon')
    ]

    @api.model
    def _default_target_group(self):
        """All selected by default"""
        return self.env['volunteer.occupation'].search([])

    @api.model
    def _default_helpee_group(self):
        return self.env['offers.helpee_group'].search([])

    state = fields.Selection(SELECT_STATES, default='unpublished', string="Stan")
    name = fields.Char(string="Nazwa")
    manager = fields.Many2one('res.users', string="Opiekun oferty")
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
        help="Opisz dlaczego wolontariusz miałby się zaangażować w tę akcję, jaki problem pomoże rozwiązać, komu pomoże. \
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
            raise exceptions.ValidationError("Liczba wakatów musi być większa od 0!")

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
            'res_model': 'offer',
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

    # Whoosh indexing section starts here
    @api.multi
    def whoosh_reindex(self):
        """
        Update/Add offers to the whoosh index.
        """
        # utility function for creating lists of names of objects
        # in a record set
        list_names = lambda rset: [r[1] for r in rset.name_get()]

        writer = search.get_writer()
        for offer in self:
            pk = unicode(offer.id)
            if offer.state == 'published':
                writer.add_document(
                    pk=pk,
                    name=offer.name,
                    wishes=list_names(offer.wishes),
                    target_group=list_names(offer.target_group),
                    project=offer.project.name
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
        writer = search.get_writer()
        for offer in self:
            writer.delete_by_term('pk', unicode(offer.id))
        writer.commit()
        return val
