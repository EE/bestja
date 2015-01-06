# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


class ProjectInvitation(models.Model):
    _name = 'bestja.project.invitation'
    _inherit = [
        'message_template.mixin',
        'ir.needaction_mixin',
        'protected_fields.mixin',
    ]
    _protected_fields = ['project', 'organization', 'description']
    _order = 'state desc, accepted_time desc, id'

    STATES = [
        ('pending', "oczekujące"),
        ('accepted', "zaakceptowane"),
    ]

    name = fields.Char(related='project.name')
    parent_organization = fields.Many2one(
        'organization',
        related='project.organization',
        ondelete='restrict',
        string="Zapraszająca organizacja",
    )
    project = fields.Many2one('bestja.project', string="Projekt")
    organization = fields.Many2one('organization', string="Organizacja")
    state = fields.Selection(STATES, default='pending', store=True, compute='compute_state', string="Stan")
    description = fields.Text(string="Opis")
    accepted_time = fields.Datetime(string="Data zaakceptowania", store=True, compute='compute_accepted_time')
    invited_projects = fields.One2many('bestja.project', inverse_name='parent_invitation')

    _sql_constraints = [
        (
            'invitation_project_organization_uniq',
            'unique(project, organization)',
            "Organizacja może zostać zaproszona do danego projektu tylko raz!"
        ),
    ]

    @api.one
    @api.constrains('organization')
    def check_organization_child(self):
        is_child = self.env['organization'].search_count([
            ('id', '=', self.organization.id),
            ('parent', '=', self.project.organization.id),
        ])
        if not is_child:
            raise exceptions.ValidationError(
                "Zaproszona organizacja musi podlegać organizacji odpowiedzialnej za projekt!"
            )

    @api.one
    @api.depends('invited_projects')
    def compute_state(self):
        self.state = 'accepted' if self.invited_projects else 'pending'

    @api.one
    @api.depends('invited_projects')
    def compute_accepted_time(self):
        invited_projects = self.invited_projects.sorted(key=lambda r: r.create_date)
        if invited_projects:
            self.accepted_time = invited_projects[0].create_date
        else:
            self.accepted_time = False

    @api.model
    def _needaction_domain_get(self):
        """
        Show pending invitations count in menu.
        """
        return [
            ('state', '=', 'pending'),
        ]

    @api.multi
    def _is_permitted(self):
        """
        You need to be a person responsible for parent project to
        change fields on invitation other than status, accepted_time.
        """
        permitted = super(ProjectInvitation, self)._is_permitted()

        return permitted \
            or self.parent_organization.coordinator == self.env.user \
            or self.project.manager == self.env.user

    @api.multi
    def accept_invitation(self):
        if self.organization.coordinator != self.env.user:
            raise exceptions.ValidationError("Nie jesteś koordynatorem zaproszonej organizacji!")

        project = self.env['bestja.project'].create({
            'parent': self.project.id,
            'name': self.project.name,
            'organization': self.env.user.coordinated_org.id,
            'date_start': self.project.date_start,
            'date_stop': self.project.date_stop,
        })

        return {
            'view_mode': 'form',
            'res_model': 'bestja.project',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'res_id': project.id,
        }


class Project(models.Model):
    _inherit = 'bestja.project'
    _parent_name = 'parent'

    parent = fields.Many2one(
        'bestja.project',
        domain="[('invitations.organization', '=', organization)]",
        string="Projekt nadrzędny",
    )
    children = fields.One2many(
        'bestja.project',
        inverse_name='parent',
    )
    invitations = fields.One2many(
        'bestja.project.invitation',
        inverse_name='project',
        groups="bestja_project.managers",
    )
    parent_invitation = fields.Many2one(
        'bestja.project.invitation',
        store=True,
        compute='compute_parent_invitation',
    )
    organization_level = fields.Integer(
        related='organization.level'
    )

    @api.one
    @api.depends('organization', 'parent')
    def compute_parent_invitation(self):
        """
        Find invitation that was used to create this project.
        """
        if not self.parent:
            self.parent_invitation = False
        else:
            parent_invitation = self.env['bestja.project.invitation'].search([
                ('organization', '=', self.organization.id),
                ('project', '=', self.parent.id),
            ])
            self.parent_invitation = parent_invitation.id


class Organization(models.Model):
    _inherit = 'organization'

    invitations = fields.One2many(
        'bestja.project.invitation',
        inverse_name='organization',
    )
