# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.osv.expression import OR

class GovernmentPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        if 'project_count' in counters:
            project_model = request.env['project.government.project']
            project_count = project_model.search_count(self._get_projects_domain(partner)) \
                if project_model.check_access_rights('read', raise_exception=False) else 0
            values['project_count'] = project_count
            
        return values

    def _get_projects_domain(self, partner):
        return [
            '|',
            ('project_manager_id.partner_id', '=', partner.id),
            '|',
            ('responsible_ministry_id.minister_id', '=', partner.id),
            ('message_follower_ids.partner_id', '=', partner.id),
        ]

    @http.route(['/my/projects', '/my/projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        project_model = request.env['project.government.project']

        domain = self._get_projects_domain(partner)

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'priority': {'label': _('Priority'), 'order': 'priority desc'},
            'progress': {'label': _('Progress'), 'order': 'progress desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'in_progress': {'label': _('In Progress'), 'domain': [('state', '=', 'in_progress')]},
            'planned': {'label': _('Planned'), 'domain': [('state', '=', 'planned')]},
            'completed': {'label': _('Completed'), 'domain': [('state', '=', 'completed')]},
        }
        searchbar_inputs = {
            'content': {'label': _('Search in Project Name'), 'input': 'content', 'domain': [('name', 'ilike', search)]},
            'code': {'label': _('Search in Code'), 'input': 'code', 'domain': [('code', 'ilike', search)]},
            'ministry': {'label': _('Search in Ministry'), 'input': 'ministry', 'domain': [('responsible_ministry_id.name', 'ilike', search)]},
            'all': {'label': _('Search in All'), 'input': 'all', 'domain': [
                '|', '|',
                ('name', 'ilike', search),
                ('code', 'ilike', search),
                ('responsible_ministry_id.name', 'ilike', search)
            ]},
        }
        searchbar_groupby = {
            'none': {'label': _('None'), 'domain': []},
            'ministry': {'label': _('Ministry'), 'domain': [], 'groupby': 'responsible_ministry_id'},
            'status': {'label': _('Status'), 'domain': [], 'groupby': 'state'},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # search
        if search and search_in:
            search_domain = searchbar_inputs[search_in]['domain']
            domain = AND([domain, search_domain])

        # pager
        projects_count = project_model.search_count(domain)
        pager = portal_pager(
            url="/my/projects",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=projects_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        if groupby == 'ministry' and not filterby:
            order = "responsible_ministry_id, %s" % order
        elif groupby == 'status' and not filterby:
            order = "state, %s" % order
            
        projects = project_model.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        if groupby:
            grouped_projects = [project_model.concat(*g) for k, g in groupbyelem(projects, itemgetter(searchbar_groupby[groupby]['groupby']))]
        else:
            grouped_projects = [projects]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'projects': projects,
            'grouped_projects': grouped_projects,
            'page_name': 'projects',
            'pager': pager,
            'default_url': '/my/projects',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("senegal_gov_project_management.portal_my_projects", values)

    @http.route(['/my/project/<int:project_id>'], type='http', auth="user", website=True)
    def portal_my_project(self, project_id=None, **kw):
        try:
            project_sudo = self._document_check_access('project.government.project', project_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._project_get_page_view_values(project_sudo, **kw)
        return request.render("senegal_gov_project_management.portal_my_project", values)

    def _project_get_page_view_values(self, project, access_token=None, **kwargs):
        values = {
            'page_name': 'project',
            'project': project,
            'user': request.env.user,
        }
        return self._get_page_view_values(project, access_token, values, 'my_projects_history', False, **kwargs)

    @http.route(['/project/qr/<model("project.government.project"):project>'], type='http', auth="public")
    def project_qr_redirect(self, project):
        """Handle QR code scanning for public access to project info"""
        if not project.exists() or project.state == 'cancelled':
            return request.render('senegal_gov_project_management.project_qr_not_found')
        
        # For public users show a limited view
        if request.env.user._is_public():
            values = {
                'project': project,
            }
            return request.render('senegal_gov_project_management.project_qr_public_view', values)
        
        # For logged in users redirect to the full project view
        return request.redirect('/web#id=%s&model=project.government.project&view_type=form' % project.id)