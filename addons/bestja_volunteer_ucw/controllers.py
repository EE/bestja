from openerp.addons.email_confirmation.controllers import AuthSignupHome
from openerp.http import request


class AuthSignupHome(AuthSignupHome):
    def get_values(self, qcontext):
        values = super(AuthSignupHome, self).get_values(qcontext)
        for field in ('languages', 'skills'):  # additional m2m fields
            if request.params.get(field):
                values[field] = [(6, 0, request.params.get(field, int))]
        return values
