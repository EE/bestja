# -*- coding: utf-8 -*-

from openerp import models, fields


class VolunteerWish(models.Model):
    _name = 'bestja.volunteer.wish'
    name = fields.Char()


class VolunteerSkill(models.Model):
    _name = 'bestja.volunteer.skill'
    name = fields.Char()


class VolunteerCertification(models.Model):
    _name = 'bestja.volunteer.certification'
    name = fields.Char()


class VolunteerDistrict(models.Model):
    _name = 'bestja.volunteer.district'
    name = fields.Char()


class VolunteerOccupation(models.Model):
    _name = 'bestja.volunteer.occupation'
    name = fields.Char()


class VolunteerLanguage(models.Model):
    _name = 'bestja.volunteer.language'
    name = fields.Char()


class DriversLicense(models.Model):
    _name = 'bestja.volunteer.drivers_license'
    name = fields.Char()


class Volunteer(models.Model):
    _inherit = 'hr.employee'

    wishes = fields.Many2many('bestja.volunteer.wish', ondelete='restrict')
    skills = fields.Many2many('bestja.volunteer.skill', ondelete='restrict')
    languages = fields.Many2many('bestja.volunteer.language', ondelete='restrict')
    certifications = fields.Many2many('bestja.volunteer.certification', ondelete='restrict')
    district = fields.Many2many('bestja.volunteer.district', ondelete='restrict')
    occupation = fields.Many2one('bestja.volunteer.occupation', ondelete='restrict')
    drivers_license = fields.Many2one('bestja.volunteer.drivers_license', ondelete='restrict')
    sanepid = fields.Datetime()
    forklift = fields.Datetime()

    street = fields.Char()
    zip_code = fields.Char(size=6)
    city = fields.Char()
    country = fields.Many2one('res.country', ondelete='restrict')
    email = fields.Char('Email')
    phone = fields.Char('Phone')
