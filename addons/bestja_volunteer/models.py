# -*- coding: utf-8 -*-

from openerp import models, fields, api


class VolunteerWish(models.Model):
    _name = 'volunteer.wish'
    name = fields.Char()


class VolunteerSkill(models.Model):
    _name = 'volunteer.skill'
    name = fields.Char()


class VolunteerCertification(models.Model):
    _name = 'volunteer.certification'
    name = fields.Char()


class VolunteerDistrict(models.Model):
    _name = 'volunteer.district'
    name = fields.Char()


class VolunteerOccupation(models.Model):
    _name = 'volunteer.occupation'
    name = fields.Char()


class VolunteerLanguage(models.Model):
    _name = 'volunteer.language'
    name = fields.Char()


class DriversLicense(models.Model):
    _name = 'volunteer.drivers_license'
    name = fields.Char()


class Volunteer(models.Model):
    _inherit = 'res.users'

    wishes = fields.Many2many('volunteer.wish', ondelete='restrict')
    skills = fields.Many2many('volunteer.skill', ondelete='restrict')
    languages = fields.Many2many('volunteer.language', ondelete='restrict')
    certifications = fields.Many2many('volunteer.certification', ondelete='restrict')
    district = fields.Many2many('volunteer.district', ondelete='restrict')
    occupation = fields.Many2one('volunteer.occupation', ondelete='restrict')
    drivers_license = fields.Many2many('volunteer.drivers_license', ondelete='restrict')
    sanepid = fields.Date()
    forklift = fields.Date()

    street = fields.Char()
    zip_code = fields.Char(size=6)
    city = fields.Char()
    country = fields.Many2one('res.country', ondelete='restrict')
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    birthdate = fields.Date()

    @api.model
    def set_default_language(self, lang_code):
        """
        Set default language for all new users.
        If the language is not already loaded
        (for example using `--load-language` option)
        it will be ignored.
        """
        lang = self.env['res.lang'].search([('code', '=', lang_code)])
        if lang:
            self.env['ir.values'].set_default('res.partner', 'lang', lang_code)
