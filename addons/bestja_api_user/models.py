# -*- coding: utf-8 -*-
from openerp import models, fields, api


class User(models.Model):
    _inherit = 'res.users'

    def __init__(self, pool, cr):
        super(User, self).__init__(pool, cr)
        self._add_permitted_fields(level='privileged', fields={'email'})
        self._add_permitted_fields(level='owner', fields={'email'})

    @api.one
    def _compute_user_access_level(self):
        """
        Access level that the current (logged in) user has for the object.
        Either "owner", "admin", "privileged" or None.
        """
        super(User, self)._compute_user_access_level()
        if not self.user_access_level and self.user_has_groups('bestja_api_user.api_access'):
            self.user_access_level = 'privileged'


class Partner(models.Model):
    _inherit = 'res.partner'

    email = fields.Char(groups='bestja_api_user.api_access')  # give access to the email field
