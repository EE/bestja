# -*- coding: utf-8 -*-

from lxml import etree

from openerp import models, fields, api, exceptions


class Offer(models.Model):
    _inherit = 'hr.job'
    _states = [
        ('open', 'not published'),
        ('recruit', 'published')
    ]

    state = fields.Selection(_states)
    vacancies = fields.Integer(string='Number of vacancies')
    project = fields.Many2one('project.project', required=True)
    skills = fields.Many2many('bestja.volunteer.skill')
    wishes = fields.Many2many('bestja.volunteer.wish')
    drivers_license = fields.Many2one('bestja.volunteer.drivers_license')
    sanepid = fields.Boolean(string="Sanepid certificate")
    forklift = fields.Boolean(string="Forklift license")

    @api.one
    @api.constrains('skills')
    def _check_skills_no(self):
        max_skills = self.env.user.company_id.bestja_max_skills
        if len(self.skills) > max_skills:
            raise exceptions.ValidationError("Choose no more than {} skills!".format(max_skills))

    @api.one
    @api.constrains('wishes')
    def _check_wishes_no(self):
        max_wishes = self.env.user.company_id.bestja_max_wishes
        if len(self.wishes) > max_wishes:
            raise exceptions.ValidationError("Choose no more than {} fields of interest!".format(max_wishes))

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
