# -*- coding: utf-8 -*-

from datetime import date
from urllib import quote_plus

from openerp import models, fields, api, exceptions


class ApplicationRejectedReason(models.Model):
    _name = 'offers.application.rejected'
    name = fields.Char(required=True)
    description = fields.Text(required=True)


class Application(models.Model):
    """
    Volunteer's request to work for an organization.
    """
    _name = 'offers.application'
    _inherit = ['message_template.mixin']
    _inherits = {
        'res.users': 'user'
    }

    STATES = [
        ('new', 'Nowa aplikacja'),
        ('meeting', 'Pierwsze spotkanie'),
        ('meeting2', 'Drugie spotkanie'),
        ('accepted', 'Zaakceptowano'),
        ('rejected', 'Odmówiono'),
    ]
    STATES_DICT = dict(STATES)

    # States that should be folded in Kanban view
    FOLDED_STATES = [
        'meeting2',
    ]
    QUALITY_CHOICES = [
        ('0', 'Brak oceny'),
        ('1', 'Słaba'),
        ('2', 'Średnia'),
        ('3', 'Dobra'),
        ('4', 'Doskonała')
    ]
    MEETING_STATES = [
        ('pending', 'Oczekujące'),
        ('accepted', 'Potwierdzone'),
        ('rejected', 'Odrzucone'),
    ]

    # The way to specify all possible groups for particular grouping in kanban
    @api.model
    def state_groups(self, present_ids, domain, **kwargs):
        folded = {key: (key in self.FOLDED_STATES) for key, _ in self.STATES}
        # Need to copy self.STATES list before returning it,
        # because odoo modifies the list it gets,
        # emptying it in the process. Bad odoo!
        return self.STATES[:], folded

    _group_by_full = {
        'state': state_groups
    }

    user = fields.Many2one('res.users', required=True, ondelete='cascade')
    offer = fields.Many2one('offer', required=True, ondelete='cascade')
    state = fields.Selection(STATES, default='new', string="Stan")
    quality = fields.Selection(QUALITY_CHOICES, string="Jakość")
    age = fields.Integer(compute='compute_age')
    meeting = fields.Datetime()
    meeting2 = fields.Datetime()
    meeting1_state = fields.Selection(MEETING_STATES, default='pending')
    meeting2_state = fields.Selection(MEETING_STATES, default='pending')
    current_meeting_state = fields.Selection(
        MEETING_STATES,
        compute='compute_current_meeting',
        inverse='inverse_current_meeting_state',
    )
    current_meeting = fields.Datetime(
        compute='compute_current_meeting',
        inverse='inverse_current_meeting',
        search='search_current_meeting'
    )
    rejected_reason = fields.Many2one('offers.application.rejected')
    notes = fields.Text()

    _sql_constraints = [
        ('user_offer_uniq', 'unique("user", "offer")', 'User can apply for an offer only once!')
    ]

    @api.model
    def send_message_new(self, record):
        record.send(
            template='bestja_offers.msg_new_application',
            recipients=record.sudo().offer.project.responsible_user,
        )

    @api.model
    def create(self, vals):
        record = super(Application, self).create(vals)
        self.send_message_new(record)
        return record

    @api.one
    @api.depends('birthdate')
    def compute_age(self):
        if self.birthdate:
            days_in_year = 365.25  # accounting for a leap year
            birthdate = fields.Date.from_string(self.birthdate)
            self.age = int((date.today() - birthdate).days / days_in_year)
        else:
            self.age = False

    @api.one
    @api.depends('state', 'meeting', 'meeting2')
    def compute_current_meeting(self):
        if self.state == 'meeting':
            self.current_meeting = self.meeting
            self.current_meeting_state = self.meeting1_state
        elif self.state == 'meeting2':
            if self.meeting2 and self.meeting2 <= self.meeting:
                raise exceptions.ValidationError("Drugie spotkanie musi odbyć się po pierwszym!")
            self.current_meeting = self.meeting2
            self.current_meeting_state = self.meeting2_state
        else:
            self.current_meeting = False
            self.current_meeting_state = False

    @api.one
    def inverse_current_meeting_state(self):
        if self.state == 'meeting2':
            self.meeting2_state = self.current_meeting_state
        else:
            self.meeting1_state = self.current_meeting_state

    @api.one
    def inverse_current_meeting(self):
        if self.state == 'meeting2':
            self.meeting2 = self.current_meeting
        elif self.state == 'meeting':
            self.meeting = self.current_meeting
        elif self.state == 'new':
            self.meeting = self.current_meeting
            self.state = 'meeting'

        # Reset the meeting state
        self.current_meeting_state = 'pending'

        # Send message about the meeting
        self.send(
            template='bestja_offers.msg_application_meeting',
            recipients=self.user,
            record_name=self.offer.name,
        )

    def search_current_meeting(self, operator, value):
        return [
            '|',  # noqa (domain indent)
                '&',
                    ('state', '=', 'meeting'),
                    ('meeting', operator, value),
                '&',
                    ('state', '=', 'meeting2'),
                    ('meeting2', operator, value),
        ]

    @api.multi
    def action_accept(self):
        for application in self:
            application.state = 'accepted'

    @api.multi
    def action_reject(self):
        for application in self:
            application.state = 'rejected'

        return {
            'name': 'Podaj powód odrzucenia',
            'view_mode': 'form',
            'res_model': 'offers.application.rejected_wizard',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }

    @api.one
    def set_rejected_reason(self, reason):
        self.rejected_reason = reason
        self.send(
            template='bestja_offers.msg_application_rejected',
            recipients=self.user,
            record_name=self.offer.name,
            sender=self.env.user,
        )

    @api.one
    def action_post_accepted(self):
        """
        After application had been accepted,
        add user to the project and the organization
        """
        offer = self.offer
        offer.project.write({
            'members': [(4, self.user.id)]
        })
        offer.sudo().project.organization.write({
            'volunteers': [(4, self.user.id)]
        })
        # Unpublish if all vacancies filled
        if offer.accepted_application_count >= offer.vacancies:
            offer.state = 'archive'
        # Send a message
        self.send(
            template='bestja_offers.msg_application_accepted',
            recipients=self.user,
            record_name=self.offer.name,
        )

    @api.one
    def action_post_unaccepted(self):
        """
        The application had been accepted, but now somebody
        changed her mind. Remove user from project, but
        leave her with the organization.
        """
        self.offer.project.write({
            'members': [(3, self.user.id)]
        })

    def _read_group_fill_results(self, cr, uid, domain, groupby, remaining_groupbys,
                                 aggregated_fields, count_field, read_group_result,
                                 read_group_order=None, context=None):
        """
        The `_read_group_fill_results` method from base model deals with creating
        custom groupings using `_group_by_full` attribute, as shown at the top
        of the class. Unfortunately it seems to support grouping using m2o fields
        only, while we want to group by a simple status field. Hence the code
        above - it replaces simple status values with so-called "m2o-like pairs".
        """
        if groupby == 'state':
            for result in read_group_result:
                state = result['state']
                result['state'] = (state, self.STATES_DICT.get(state))

        return super(Application, self)._read_group_fill_results(
            cr, uid, domain, groupby, remaining_groupbys, aggregated_fields,
            count_field, read_group_result, read_group_order, context
        )

    @api.multi
    def get_meeting_confirmation_link(self, resolution):
        """
        Applicants can use this url to confirm a meeting.
        resolution -- one of 'accepted', 'rejected'
        """
        return '{}meeting/{}/?time={}'.format(
            self.offer.get_public_url(),
            resolution,
            quote_plus(self.current_meeting),
        )


class UserWithApplications(models.Model):
    _inherit = 'res.users'

    applications = fields.One2many(
        'offers.application',
        inverse_name='user'
    )
