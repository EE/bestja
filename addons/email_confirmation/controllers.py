# -*- coding: utf-8 -*-
import logging
import openerp
from openerp.addons.auth_signup.res_users import SignupError
from openerp import http
from openerp.http import request
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class AuthSignupHome(openerp.addons.web.controllers.main.Home):
    _inherit = "openerp.addons.auth_signup.controllers.main.AuthSignupHome"

    @http.route('/web/authenticate', type='http', auth='public', website=True)
    def web_auth_authenticate(self, *args, **kw):
        """After signing up user confirms his email"""
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            return http.request.not_found()
        else:
            try:
                values = dict((key, qcontext.get(key)) for key in ('login', 'email'))
                request.env['res.users'].sudo().authenticate_after_confirmation(values, qcontext.get('token'))
                request.cr.commit()

                response = super(AuthSignupHome, self).web_login(*args, **kw)
                response.qcontext['message'] = "Twoje konto zostało poprawnie aktywowane. Możesz się zalogować."
                return response
            except (SignupError, AssertionError), e:
                qcontext['error'] = _(e.message)
        return self.web_login(*args, **kw)

    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        """Need to override, as parent function logs the user in"""
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            return http.request.not_found()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                qcontext['message'] = \
                    "Na twój e-mail został przesłany link aktywacyjny. Kliknij go, aby móc się zalogować."
                # do not login user here
            except (SignupError, AssertionError), e:
                message = e.message
                if message.startswith('duplicate key value violates unique constraint "res_users_login_key"'):
                    message = "Podany adres e-mail jest już używany."
                qcontext['error'] = _(message)

        return request.render('auth_signup.signup', qcontext)

    def do_signup(self, qcontext):
        """ overriden to include redirect """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password')}
        assert all(values.values()), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Podane hasła się różnią."
        request.env['res.users'].sudo().with_context(
            redirect=qcontext.get('redirect'),
            no_reset_password=True,
            confirm_signup=True
        ).signup(values, qcontext.get('token'))
        request.cr.commit()
