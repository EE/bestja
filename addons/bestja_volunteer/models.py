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


class Voivodeship(models.Model):
    _name = 'volunteer.voivodeship'
    name = fields.Char()


class Volunteer(models.Model):
    _inherit = 'res.users'

    wishes = fields.Many2many(
        'volunteer.wish',
        string="Zainteresowania",
        ondelete='restrict',
        groups="bestja_base.instance_admin",
    )
    skills = fields.Many2many('volunteer.skill', groups="bestja_base.instance_admin", ondelete='restrict')
    languages = fields.Many2many('volunteer.language', groups="bestja_base.instance_admin", ondelete='restrict')
    certifications = fields.Many2many(
        'volunteer.certification',
        groups="bestja_base.instance_admin",
        ondelete='restrict'
    )
    district = fields.Many2many('volunteer.district', groups="bestja_base.instance_admin", ondelete='restrict')
    occupation = fields.Many2one('volunteer.occupation', groups="bestja_base.instance_admin", ondelete='restrict')
    drivers_license = fields.Many2many(
        'volunteer.drivers_license',
        groups="bestja_base.instance_admin",
        ondelete='restrict'
    )
    sanepid = fields.Date(groups="bestja_base.instance_admin")
    forklift = fields.Date(groups="bestja_base.instance_admin")

    # mailing address
    street_gov = fields.Char(string="Ulica", groups='bestja_base.instance_admin')
    street_number_gov = fields.Char(string="Numer budynku", groups='bestja_base.instance_admin')
    apt_number_gov = fields.Char(string="mieszk.", groups='bestja_base.instance_admin')
    zip_code_gov = fields.Char(size=6, string="Kod pocztowy", groups='bestja_base.instance_admin')
    city_gov = fields.Char(string="Miejscowość", groups='bestja_base.instance_admin')
    voivodeship_gov = fields.Many2one(
        'volunteer.voivodeship',
        string="Województwo",
        groups='bestja_base.instance_admin'
    )
    country_gov = fields.Many2one(
        'res.country',
        ondelete='restrict',
        string="Kraj",
        groups='bestja_base.instance_admin'
    )
    email = fields.Char('Email', groups="bestja_base.instance_admin")
    phone = fields.Char('Phone', groups="bestja_base.instance_admin")
    birthdate = fields.Date(groups="bestja_base.instance_admin")

    curriculum_vitae = fields.Binary(string="CV", groups="bestja_base.instance_admin")
    cv_filename = fields.Char(groups="bestja_base.instance_admin")

    different_addresses = fields.Boolean(
        default=False,
        groups='bestja_base.instance_admin',
        string="Adres zamieszkania jest inny niż zameldowania",
    )
    # address of residence
    street = fields.Char(string="Ulica", groups='bestja_base.instance_admin')
    street_number = fields.Char(string="Numer budynku", groups='bestja_base.instance_admin')
    apt_number = fields.Char(string="mieszk.", groups='bestja_base.instance_admin')
    zip_code = fields.Char(size=6, string="Kod pocztowy", groups='bestja_base.instance_admin')
    city = fields.Char(string="Miejscowość", groups='bestja_base.instance_admin')
    voivodeship = fields.Many2one(
        'volunteer.voivodeship',
        groups='bestja_base.instance_admin',
        string="Województwo",
    )
    country = fields.Many2one(
        'res.country',
        ondelete='restrict',
        groups='bestja_base.instance_admin',
        string="Kraj",
    )
    daypart = fields.Many2many('volunteer.daypart', groups="bestja_base.instance_admin", string="pora dnia")
    daypart_comments = fields.Text(string="Uwagi", groups="bestja_base.instance_admin")

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

    @staticmethod
    def is_password_safe(password):
        """
        Does password follow the security rules?
        """
        return len(password) > 6 and re.search('[a-zA-Z]+', password) \
            and not password.islower() and not password.isupper()

    @api.model
    def signup(self, values, token=None):
        """
        Added for password validation: at least 6 characters, any letters,
        any uppercase letter, not only lowercase.
        You can't do it using constraints, as password is hashed in the database.
        """
        if not self.is_password_safe(values.get('password')):
            raise SignupError("Hasło powinno zawierać co najmniej 6 znaków, w tym litery różnej wielkości!")
        return super(Volunteer, self).signup(values, token)

    @api.model
    def change_password(self, old_passwd, new_passwd):
        """
        For changing password in preferences.
        """
        if not self.is_password_safe(new_passwd):
            raise exceptions.ValidationError(
                "Hasło powinno zawierać co najmniej 6 znaków, w tym litery różnej wielkości!"
            )
        return super(Volunteer, self).change_password(old_passwd, new_passwd)

    @api.onchange('different_addresses')
    def equal_addresses(self):
        """
        If mailing address is the same as address of residence
        than it should be empty.
        """
        if not self.different_addresses:
            self.street_gov = None
            self.street_number_gov = None
            self.apt_number_gov = None
            self.zip_code_gov = None
            self.city_gov = None
            self.country_gov = None
            self.voivodeship_gov = None

    @api.onchange('country', 'country_gov')
    def onchange_country(self):
        """
        If the chosen country is not Poland, reset voivodeship
        """
        if self.country.code != 'PL':
            self.voivodeship = None
        if self.country_gov.code != 'PL':
            self.voivodeship_gov = None

        return {
            'domain': {
                # [] = full list; [('id', '=', False)] = empty list
                'voivodeship': [] if self.country.code == 'PL' else [('id', '=', False)],
                'voivodeship_gov': [] if self.country_gov.code == 'PL' else [('id', '=', False)]
            }
        }
