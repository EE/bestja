# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


class ApplicationWizardMixin():
    @staticmethod
    def default_func(field):
        """Returns a function, that in turns returns
        a default value for a field `field`."""
        def func(self):
            active_id = self.env.context['active_id']
            if active_id:
                application = self.env['offers.application'].browse([active_id])
                return getattr(application, field)
        return func

    application = fields.Many2one(
        'offers.application',
        required=True,
        default=lambda self: self.env.context['active_id']
    )


class ApplicationMeetingWizard(ApplicationWizardMixin, models.TransientModel):
    _name = 'offers.application.meeting_wizard'

    meeting = fields.Datetime(
        string=u"Termin spotkania",
        default=ApplicationWizardMixin.default_func('current_meeting')
    )

    @api.one
    def save_date(self):
        if self.meeting and self.meeting <= fields.Datetime.now():
            raise exceptions.ValidationError("Data spotkania musi być w przyszłości!")
        self.application.current_meeting = self.meeting


class ApplicationRejectedWizard(ApplicationWizardMixin, models.TransientModel):
    _name = 'offers.application.rejected_wizard'

    reason = fields.Many2one(
        'offers.application.rejected',
        string=u"Powód",
        required=True,
        default=ApplicationWizardMixin.default_func('rejected_reason')
    )

    @api.one
    def save_reason(self):
        self.application.set_rejected_reason(self.reason)


class ApplicationNotesWizard(ApplicationWizardMixin, models.TransientModel):
    _name = 'offers.application.notes_wizard'

    notes = fields.Text(
        string=u"Notatka",
        default=ApplicationWizardMixin.default_func('notes')
    )

    @api.one
    def save_notes(self):
        self.application.notes = self.notes
