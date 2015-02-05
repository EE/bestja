from openerp import http
from openerp.addons.email_confirmation.controllers import AuthSignupHome


class AgeAuthSignupHome(AuthSignupHome):
    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        response = super(AgeAuthSignupHome, self).web_auth_signup(*args, **kw)
        min_age = http.request.env['ir.config_parameter'].get_param('bestja_age_verification.min_age')
        response.qcontext['min_age'] = min_age
        return response
