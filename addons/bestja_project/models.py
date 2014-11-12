# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Project(models.Model):
    _name = 'bestja.project'

    def current_members(self):
        """
        Limit to members of the current organization only.
        """
        try:
            # try to use organization configured in the current project
            project = self.browse([self.env.context['params']['id']])
            organization = project.organization
        except KeyError:
            # most likely a new project, use organization the user coordinates
            organization = self.env.user.coordinated_org
        return [('id', 'in', organization.volunteers.ids)]

    name = fields.Char(required=True, string="Nazwa")
    organization = fields.Many2one(
        'organization',
        default=api.model(lambda self: self.env.user.coordinated_org),
        required=True,
        string="Organizacja",
        domain=lambda self: [('coordinator', '=', self.env.user.id)],
    )
    manager = fields.Many2one(
        'res.users',
        required=True,
        domain=current_members,
        string="Menadżer projektu",
    )
    date_start = fields.Date(required=True, string="od dnia")
    date_stop = fields.Date(required=True, string="do dnia")
    members = fields.Many2many(
        'res.users',
        relation='project_members_rel',
        column1='project',
        column2='member',
        domain=current_members,
        string="Zespół"
    )
    tasks = fields.One2many('bestja.task', 'project', string="Zadania")
    tasks_count = fields.Integer(compute='_tasks_count', string="Liczba zadań")
    done_tasks_count = fields.Integer(compute='_tasks_count', string="Liczba skończonych zadań")

    @api.one
    @api.depends('tasks')
    def _tasks_count(self):
        self.tasks_count = len(self.tasks)
        self.done_tasks_count = self.tasks.search_count([
            ('project', '=', self.id),
            ('state', '=', 'done')
        ])


class Task(models.Model):
    _name = 'bestja.task'
    _order = 'state desc'
    STATES = [
        ('new', "nowe"),
        ('in_progress', "w trakcie realizacji"),
        ('done', "zrealizowane"),
    ]

    def current_project_members(self):
        """
        Returns a domain selecting members of the current project.
        """
        active_id = self.env.context.get('active_id')
        if active_id is None:
            return []
        project = self.env['bestja.project'].browse([active_id])
        return [('id', 'in', project.members.ids)]

    name = fields.Char(required=True, string="Nazwa zadania")
    state = fields.Selection(STATES, default='new', string="Status")
    user = fields.Many2one(
        'res.users',
        domain=current_project_members,
        string="Wykonawca zadania",
    )
    date_start = fields.Date(required=True, string="od dnia")
    date_stop = fields.Date(required=True, string="do dnia")
    description = fields.Text(string="Opis zadania")
    project = fields.Many2one(
        'bestja.project',
        required=True,
        ondelete='cascade',
        string="Projekt",
    )

    @api.one
    def set_in_progress(self):
        self.state = 'in_progress'

    @api.one
    def set_done(self):
        self.state = 'done'


class UserWithProjects(models.Model):
    _inherit = 'res.users'

    projects = fields.Many2many(
        'bestja.project',
        relation='project_members_rel',
        column1='member',
        column2='project',
        string="Projekty"
    )
