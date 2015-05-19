# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


class ApplicationWizardMixin():
    @staticmethod
    def default_func(field):
        """Returns a function, that in turns returns
        a default value for a field `field`."""
        def func(self):
            active_id = self.env.context.get('active_id')
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

    def default_place(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            application = self.env['offers.application'].browse([active_id])
            if application.current_meeting_place:
                return application.current_meeting_place

            return application.sudo().offer.organization.address

    meeting = fields.Datetime(
        string=u"Termin spotkania",
        required=True,
        default=ApplicationWizardMixin.default_func('current_meeting')
    )
    meeting_place = fields.Text(
        string=u"Miejsce spotkania",
        required=True,
        default=default_place,
    )

    @api.one
    def save_date(self):
        if self.meeting and self.meeting <= fields.Datetime.now():
            raise exceptions.ValidationError("Data spotkania musi być w przyszłości!")
        self.application.current_meeting = self.meeting
        self.application.current_meeting_place = self.meeting_place

        # Send message about the meeting
        self.application.send(
            template='bestja_offers.msg_application_meeting',
            recipients=self.application.user,
            record_name=self.application.offer.name,
            sender=self.env.user,
        )


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
