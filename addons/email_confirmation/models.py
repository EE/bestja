# -*- coding: utf-8 -*-

import urllib
import urlparse

from openerp import api, models, fields
from openerp.addons.auth_signup.res_users import now


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_signup_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        """ redirect added """
        urls = super(Partner, self)._get_signup_url_for_action(action, view_type, menu_id, res_id, model)
        redirect = self.env.context.get('redirect')
        if not redirect:
            return urls
        for partner_id, url in urls.iteritems():
            if url:
                url = urlparse.urlparse(urls[partner_id])
                querydict = urlparse.parse_qs(url.query)
                querydict['redirect'] = redirect
                new_url = urlparse.urlunparse((
                    url.scheme,
                    url.netloc,
                    url.path,
                    url.params,
                    urllib.urlencode(querydict, doseq=True),
                    url.fragment,
                ))
                urls[partner_id] = new_url
        return urls


class Users(models.Model):
    _inherit = "res.users"

    STATES = [
        ('active', 'aktywny'),
        ('not_activated', 'nieaktywowany')
    ]

    active_state = fields.Selection(STATES, default='active', store=True, string="Stan")

    @api.model
    def authenticate_after_confirmation(self, values, token=None):
        if token:
            # signup with a token: find the corresponding partner id
            partner = self.env['res.partner']._signup_retrieve_partner(token, check_validity=True, raise_exception=True)
            # invalidate signup token
            partner.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False})
            # activate user
            user = self.env['res.users'].search([('partner_id', '=', partner.id), ('active', '=', False)])
            if user:
                user.active = True
                user.active_state = 'active'

    @api.model
    def create(self, values):
        user = super(Users, self).create(values)
        # user is not active yet, he needs to click a link in the email
        if self.env.context.get('confirm_signup'):
            user.active = False
            user.active_state = 'not_activated'
            user.partner_id.signup_prepare(signup_type="authenticate", expiration=now(days=+1))
            redirect_url = self.env.context.get('redirect')
            template = self.with_context(redirect=redirect_url).env.ref('email_confirmation.user_confirmation_email')
            template.send_mail(user.id, force_send=True, raise_exception=True)
        return user
