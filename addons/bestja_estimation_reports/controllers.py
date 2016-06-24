from collections import defaultdict

from openerp import http
from openerp.fields import Date
from werkzeug import exceptions


class DetailedStats(http.Controller):
    @http.route('/estimated', auth='user', website=True)
    def projects_list(self):
        if not http.request.env.user.sudo(http.request.env.user). \
                user_has_groups('bestja_project.managers'):
            return exceptions.Forbidden()

        projects = http.request.env['bestja.project'].sudo().search([
            ('organization_level', '=', 0),
            ('use_estimation_reports', '=', True),
            ('date_start', '<=', Date.today()),
        ], order='date_start desc')

        return http.request.render('bestja_estimation_reports.projects_list', {
            'projects': projects,
        })

    def group_data_by_organization(self, data):
        """
        Get data from SQL query and group it by organizations and days.
        """
        sums = []
        day_tonnages = None
        last_id = None
        for item in data:
            current_id, name, date, tonnage = item

            if current_id != last_id:
                day_tonnages = defaultdict(int)
                sums.append({
                    'id': current_id,
                    'name': name,
                    'tonnages': day_tonnages,
                })
                last_id = current_id
            day_tonnages[date] = tonnage
        return sums

    def get_store_days(self, project_id):
        """
        Get dates from stores in project `project_id`
        """
        http.request.env.cr.execute("""
            SELECT day.date
            FROM bestja_stores_day as day
            JOIN bestja_stores_store_in_project as store ON (day.store = store.id)
            WHERE store.top_project = %s
            GROUP BY day.date
            ORDER BY day.date ASC
        """, [project_id, ])
        return http.request.env.cr.fetchall()

    @http.route('/estimated/<int:project>', auth='user', website=True)
    def by_bank(self, project):
        if not http.request.env.user.sudo(http.request.env.user). \
                user_has_groups('bestja_project.managers'):
            return exceptions.Forbidden()

        days = self.get_store_days(project)

        http.request.env.cr.execute("""
            SELECT responsible.id, responsible.name, day.date,
                SUM(entry.tonnage) as sum_tonnage
            FROM bestja_estimation_report_entry as entry
            JOIN organization as responsible ON (entry.responsible_organization = responsible.id)
            JOIN bestja_stores_day as day ON (entry.day_in_store = day.id)
            JOIN bestja_estimation_report as report ON (entry.estimation_report = report.id)
            WHERE entry.top_project = %s AND report.state = 'sent'
            GROUP BY responsible.id, responsible.name, day.date
            ORDER BY sum_tonnage DESC, responsible.name ASC, day.date ASC
        """, [project, ])
        bank_sums = http.request.env.cr.fetchall()

        return http.request.render('bestja_estimation_reports.by_bank', {
            'project': http.request.env['bestja.project'].sudo().browse([project, ]),
            'bank_sums': self.group_data_by_organization(bank_sums),
            'days': days,
        })

    @http.route('/estimated/<int:project>/<int:organization>', auth='user', website=True)
    def by_org(self, project, organization):
        if not http.request.env.user.sudo(http.request.env.user). \
                user_has_groups('bestja_project.managers'):
            return exceptions.Forbidden()

        days = self.get_store_days(project)

        http.request.env.cr.execute("""
            SELECT organization.id, organization.name, day.date,
                SUM(entry.tonnage) as sum_tonnage
            FROM bestja_estimation_report_entry as entry
            JOIN organization ON (entry.organization = organization.id)
            JOIN bestja_stores_day as day ON (entry.day_in_store = day.id)
            JOIN bestja_estimation_report as report ON (entry.estimation_report = report.id)
            WHERE entry.top_project = %s AND entry.responsible_organization = %s
                AND report.state = 'sent'
            GROUP BY organization.id, organization.name, day.date
            ORDER BY sum_tonnage DESC, organization.name ASC, day.date ASC
        """, [project, organization])
        org_sums = http.request.env.cr.fetchall()

        return http.request.render('bestja_estimation_reports.by_org', {
            'project': http.request.env['bestja.project'].sudo().browse([project, ]),
            'organization': http.request.env['organization'].sudo().browse([organization, ]),
            'org_sums': self.group_data_by_organization(org_sums),
            'days': days,
        })
