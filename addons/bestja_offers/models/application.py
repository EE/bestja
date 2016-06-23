# -*- coding: utf-8 -*-

from datetime import date
from urllib import quote_plus
import operator

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

    STATES = [
        ('new', u'Nowa aplikacja'),
        ('meeting', u'Pierwsze spotkanie'),
        ('meeting2', u'Drugie spotkanie'),
        ('accepted', u'Zaakceptowano'),
        ('rejected', u'Odmówiono'),
    ]
    STATES_DICT = dict(STATES)

    # States that should be folded in Kanban view
    FOLDED_STATES = [
        'meeting2',
    ]
    QUALITY_CHOICES = [
        ('0', u'Brak oceny'),
        ('1', u'Słaba'),
        ('2', u'Średnia'),
        ('3', u'Dobra'),
        ('4', u'Doskonała')
    ]
    MEETING_STATES = [
        ('pending', u'Oczekujące'),
        ('accepted', u'Potwierdzone'),
        ('rejected', u'Odrzucone'),
    ]

    # The way to specify all possible groups for particular grouping in kanban
    @api.model
    def _state_groups(self, present_ids, domain, **kwargs):
        folded = {key: (key in self.FOLDED_STATES) for key, _ in self.STATES}
        # Need to copy self.STATES list before returning it,
        # because odoo modifies the list it gets,
        # emptying it in the process. Bad odoo!
        return self.STATES[:], folded

    _group_by_full = {
        'state': _state_groups
    }

    user = fields.Many2one('res.users', required=True, ondelete='cascade')
    offer = fields.Many2one('offer', required=True, ondelete='cascade')
    state = fields.Selection(STATES, default='new', string=u"Stan")
    quality = fields.Selection(QUALITY_CHOICES, string=u"Jakość")
    age = fields.Integer(compute='_compute_age')
    meeting = fields.Datetime()
    meeting2 = fields.Datetime()
    meeting1_state = fields.Selection(MEETING_STATES, default='pending')
    meeting2_state = fields.Selection(MEETING_STATES, default='pending')
    meeting1_place = fields.Text()
    meeting2_place = fields.Text()
    current_meeting_state = fields.Selection(
        MEETING_STATES,
        compute='_compute_current_meeting',
        inverse='_inverse_current_meeting_state',
    )
    current_meeting = fields.Datetime(
        compute='_compute_current_meeting',
        inverse='_inverse_current_meeting',
        search='_search_current_meeting'
    )
    current_meeting_place = fields.Text(
        compute='_compute_current_meeting',
        inverse='_inverse_current_meeting_place',
    )
    rejected_reason = fields.Many2one('offers.application.rejected')
    notes = fields.Text()

    # Fields from user model
    name = fields.Char(related='user.name', related_sudo=True)
    occupation = fields.Many2one('volunteer.occupation', related='user.occupation', related_sudo=True)
    phone = fields.Char(related='user.phone', related_sudo=True)
    email = fields.Char(related='user.user_email', related_sudo=True)
    city_gov = fields.Char(related='user.city_gov', related_sudo=True)
    city = fields.Char(related='user.city', related_sudo=True)
    different_addresses = fields.Boolean(related='user.different_addresses', related_sudo=True)
    skills = fields.Many2many('volunteer.skill', related='user.skills', related_sudo=True)
    languages = fields.Many2many('volunteer.language', related='user.languages', related_sudo=True)
    wishes = fields.Many2many('volunteer.wish', related='user.wishes', related_sudo=True)
    curriculum_vitae = fields.Binary(related='user.curriculum_vitae', related_sudo=True)
    cv_filename = fields.Char(related='user.cv_filename', related_sudo=True)
    image = fields.Binary(related='user.image', related_sudo=True)
    image_medium = fields.Binary(related='user.image_medium', related_sudo=True)

    _sql_constraints = [
        ('user_offer_uniq', 'unique("user", "offer")', 'User can apply for an offer only once!')
    ]

    @api.one
    def _send_message_new(self):
        self.send(
            template='bestja_offers.msg_new_application',
            recipients=self.sudo().offer.project.responsible_user,
        )

    @api.model
    def create(self, vals):
        record = super(Application, self).create(vals)
        record._send_message_new()
        return record

    @api.one
    @api.depends('user.birthdate')
    def _compute_age(self):
        if self.user.birthdate:
            days_in_year = 365.25  # accounting for a leap year
            birthdate = fields.Date.from_string(self.user.birthdate)
            self.age = int((date.today() - birthdate).days / days_in_year)
        else:
            self.age = False

    @api.one
    @api.depends('state', 'meeting', 'meeting2')
    def _compute_current_meeting(self):
        if self.state == 'meeting':
            self.current_meeting = self.meeting
            self.current_meeting_state = self.meeting1_state
            self.current_meeting_place = self.meeting1_place
        elif self.state == 'meeting2':
            if self.meeting2 and self.meeting2 <= self.meeting:
                raise exceptions.ValidationError("Drugie spotkanie musi odbyć się po pierwszym!")
            self.current_meeting = self.meeting2
            self.current_meeting_state = self.meeting2_state
            self.current_meeting_place = self.meeting2_place
        else:
            self.current_meeting = False
            self.current_meeting_state = False
            self.current_meeting_place = False

    @api.one
    def _inverse_current_meeting_state(self):
        if self.state == 'meeting2':
            self.meeting2_state = self.current_meeting_state
        else:
            self.meeting1_state = self.current_meeting_state

    @api.one
    def _inverse_current_meeting_place(self):
        if self.state == 'meeting2':
            self.meeting2_place = self.current_meeting_place
        else:
            self.meeting1_place = self.current_meeting_place

    @api.one
    def _inverse_current_meeting(self):
        if self.state == 'meeting2':
            self.meeting2 = self.current_meeting
        elif self.state == 'meeting':
            self.meeting = self.current_meeting
        elif self.state == 'new':
            self.meeting = self.current_meeting
            self.state = 'meeting'

        # Reset the meeting state
        self.current_meeting_state = 'pending'

    def _search_current_meeting(self, operator, value):
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

    @api.multi
    def show_profile(self):
        return {
            'name': 'Profil użytkownika',
            'view_mode': 'form',
            'res_model': 'res.users',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'self',
            'res_id': self.user.id,
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
    def confirm_meeting(self):
        self.current_meeting_state = 'accepted'

        self.send(
            template='bestja_offers.msg_application_meeting_accepted',
            recipients=self.offer.project.responsible_user,
            sender=self.env.user,
        )

    @api.one
    def reject_meeting(self):
        self.current_meeting_state = 'rejected'

        self.send(
            template='bestja_offers.msg_application_meeting_rejected',
            recipients=self.offer.project.responsible_user,
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

    @api.model
    def _get_access_link(self, mail, partner):
        """
        Link to object in e-mail should depend on the recipient - administrators, coordinators and managers should
        get internal links, while normal users should only see public offers.
        """
        if mail.mail_message_id.res_id:
            offer = self.env['offers.application'].sudo().browse([mail.mail_message_id.res_id]).offer
            recipient_ids = (r.user_ids.ids for r in mail.recipient_ids)
            recipient_ids = reduce(operator.add, recipient_ids)  # Flaten the list
            admin_ids = self.env.ref('bestja_base.instance_admin').users.ids
            recipient_is_admin = bool(set(admin_ids) & set(recipient_ids))
            if not recipient_is_admin and offer.project.manager.id not in recipient_ids \
                    and offer.organization.coordinator.id not in recipient_ids:
                return offer.get_public_url()
        # we are sending this to coordinator / manager, give an internal link
        return super(Application, self)._get_access_link(mail, partner)

    @api.model
    def message_redirect_action(self):
        """
        Similar to _get_access_link, but for links in Odoo inbox.
        """
        params = self.env.context.get('params')
        if params and params.get('res_id'):
            offer = self.env['offers.application'].sudo().browse([params.get('res_id')]).offer
            if not self.user_has_groups('bestja_base.instance_admin') and offer.project.manager != self.env.user and offer.organization.coordinator != self.env.user:
                return {
                    'type': 'ir.actions.act_url',
                    'url': offer.get_public_url(),
                    'target': 'self',
                }
        return super(Application, self).message_redirect_action()


class UserWithApplications(models.Model):
    _inherit = 'res.users'

    applications = fields.One2many(
        'offers.application',
        inverse_name='user'
    )
