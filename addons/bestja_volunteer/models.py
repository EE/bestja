# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
from openerp.addons.auth_signup.res_users import SignupError
import re


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


class Daypart(models.Model):
    _name = 'volunteer.daypart'
    name = fields.Char(required=True)


class Volunteer(models.Model):
    _inherit = 'res.users'

    wishes = fields.Many2many('volunteer.wish', string="Zainteresowania", ondelete='restrict')
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

    curriculum_vitae = fields.Binary(string="CV")
    cv_filename = fields.Char()

    daypart = fields.Many2many('volunteer.daypart', string="pora dnia")

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

    @api.one
    def sync_group(self, group, domain):
        """
        if the current user satisfies the domain `domain` she should be a member
        of a group `group`. Otherwise she should be removed.
        """
        results = self.search_count(domain + [('id', '=', self.id)])
        command = 4 if results else 3  # add if true else remove
        self.sudo().write({
            'groups_id': [(command, group.id)],
        })

    def check_password_rules(self, password):
        """ Returns true if password is incorrect """
        if (len(password) < 6 or not re.search('[a-zA-Z]+', password)
                or password.islower() or password.isupper()):
                return True
        return False

    @api.model
    def signup(self, values, token=None):
        """
            Added for password validation: at least 6 characters, any letters,
            any uppercase letter, not only lowercase.
            You can't do it using constraints, as password is hashed in the database.
        """
        if self.check_password_rules(values.get('password')):
            raise SignupError("Hasło powinno zawierać co najmniej 6 znaków, w tym litery różnej wielkości!")
        return super(Volunteer, self).signup(values, token)

    @api.model
    def change_password(self, old_passwd, new_passwd):
        """
            For changing password in preferences.
        """
        if self.check_password_rules(new_passwd):
            raise exceptions.ValidationError("Hasło powinno zawierać co najmniej 6 znaków, w tym litery różnej wielkości!")
        return super(Volunteer, self).change_password(old_passwd, new_passwd)
