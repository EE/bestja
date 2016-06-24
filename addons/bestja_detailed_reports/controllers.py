from openerp import http
from openerp.fields import Date
from werkzeug import exceptions


class DetailedStats(http.Controller):
    @http.route('/detailed', auth='user', website=True)
    def projects_list(self):
        if not http.request.env.user.sudo(http.request.env.user). \
                user_has_groups('bestja_project.managers'):
            return exceptions.Forbidden()

        projects = http.request.env['bestja.project'].sudo().search([
            ('organization_level', '=', 0),
            ('use_detailed_reports', '=', True),
            ('date_start', '<=', Date.today()),
        ], order='date_start desc')

        return http.request.render('bestja_detailed_reports.projects_list', {
            'projects': projects,
        })

    @http.route('/detailed/<int:project>', auth='user', website=True)
    def by_bank(self, project):
        if not http.request.env.user.sudo(http.request.env.user). \
                user_has_groups('bestja_project.managers'):
            return exceptions.Forbidden()

        http.request.env.cr.execute("""
            SELECT responsible.id, responsible.name, SUM(entry.total_cities_nr) as cities_nr,
                SUM(entry.tonnage) as sum_tonnage
            FROM bestja_report_entry as entry
            JOIN organization as responsible ON (entry.responsible_organization = responsible.id)
            JOIN bestja_detailed_report as report ON (entry.detailed_report = report.id)
            WHERE entry.top_project = %s AND report.state = 'accepted'
            GROUP BY responsible.id, responsible.name
            ORDER BY sum_tonnage DESC, responsible.name ASC
        """, [project, ])
        bank_sums = http.request.env.cr.fetchall()

        return http.request.render('bestja_detailed_reports.by_bank', {
            'project': http.request.env['bestja.project'].sudo().browse([project, ]),
            'bank_sums': bank_sums,
        })

    @http.route('/detailed/<int:project>/<int:organization>', auth='user', website=True)
    def by_org(self, project, organization):
        if not http.request.env.user.sudo(http.request.env.user). \
                user_has_groups('bestja_project.managers'):
            return exceptions.Forbidden()

        http.request.env.cr.execute("""
            SELECT organization.id, organization.name,
                SUM(entry.tonnage) as sum_tonnage
            FROM bestja_report_entry as entry
            JOIN organization ON (entry.organization = organization.id)
            JOIN bestja_detailed_report as report ON (entry.detailed_report = report.id)
            WHERE entry.top_project = %s AND entry.responsible_organization = %s
                AND report.state = 'accepted'
            GROUP BY organization.id, organization.name
            ORDER BY sum_tonnage DESC, organization.name ASC
        """, [project, organization])
        org_sums = http.request.env.cr.fetchall()

        return http.request.render('bestja_detailed_reports.by_org', {
            'project': http.request.env['bestja.project'].sudo().browse([project, ]),
            'organization': http.request.env['organization'].sudo().browse([organization, ]),
            'org_sums': org_sums,
        })
