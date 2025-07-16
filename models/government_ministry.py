# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class GovernmentMinistry(models.Model):
    _name = 'government.ministry'
    _description = 'Government Ministry'
    _inherit = ['gov.qr.code.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char('Ministry Name', required=True, tracking=True)
    code = fields.Char('Ministry Code', tracking=True)
    active = fields.Boolean(default=True)
    description = fields.Text('Description')
    
    minister_id = fields.Many2one('res.partner', string='Minister', 
                                 tracking=True, domain=[('is_company', '=', False)])
    minister_title = fields.Char('Minister Title')
    minister_phone = fields.Char('Minister Phone')
    minister_email = fields.Char('Minister Email')
    
    projects_responsible_ids = fields.One2many('project.government.project', 
                                              'responsible_ministry_id', 
                                              string='Responsible Projects')
    projects_involved_ids = fields.Many2many('project.government.project', 
                                            'project_ministry_involved_rel',
                                            'ministry_id', 'project_id',
                                            string='Involved Projects')
    
    decision_ids = fields.Many2many('government.decision', 
                                  'ministry_decision_rel',
                                  'ministry_id', 'decision_id',
                                  string='Related Decisions')
    
    logo = fields.Binary('Ministry Logo', attachment=True)
    address = fields.Text('Address')
    phone = fields.Char('Phone')
    email = fields.Char('Email')
    website = fields.Char('Website')
    
    department_count = fields.Integer(compute='_compute_department_count')
    project_count = fields.Integer(compute='_compute_project_count')
    
    company_id = fields.Many2one('res.company', string='Company', 
                               default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Ministry code must be unique!')
    ]
    
    @api.depends('projects_responsible_ids')
    def _compute_project_count(self):
        for ministry in self:
            ministry.project_count = len(ministry.projects_responsible_ids) + len(ministry.projects_involved_ids)
    
    def _compute_department_count(self):
        for ministry in self:
            # This is a placeholder for potential future functionality
            # Could be extended to track departments within ministries
            ministry.department_count = 0
            
    def action_view_projects(self):
        self.ensure_one()
        return {
            'name': _('Ministry Projects'),
            'view_mode': 'tree,form,kanban',
            'res_model': 'project.government.project',
            'domain': ['|', ('responsible_ministry_id', '=', self.id), 
                       ('coordinating_ministries_ids', 'in', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_responsible_ministry_id': self.id}
        }