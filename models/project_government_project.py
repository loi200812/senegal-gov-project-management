# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class ProjectGovernmentProject(models.Model):
    _name = 'project.government.project'
    _description = 'Government Project'
    _inherit = ['gov.qr.code.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, id desc'

    name = fields.Char('Project Name', required=True, tracking=True)
    code = fields.Char('Project Code', tracking=True)
    description = fields.Text('Description', tracking=True)
    
    start_date = fields.Date('Planned Start Date', tracking=True)
    end_date = fields.Date('Planned End Date', tracking=True)
    actual_start_date = fields.Date('Actual Start Date', tracking=True)
    actual_end_date = fields.Date('Actual End Date', tracking=True)
    
    duration = fields.Integer('Planned Duration (days)', compute='_compute_duration', store=True)
    actual_duration = fields.Integer('Actual Duration (days)', compute='_compute_actual_duration', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('awaiting_decision', 'Awaiting Decision'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    responsible_ministry_id = fields.Many2one('government.ministry', 
                                           string='Responsible Ministry', 
                                           tracking=True)
    
    coordinating_ministries_ids = fields.Many2many('government.ministry', 
                                                'project_ministry_involved_rel',
                                                'project_id', 'ministry_id',
                                                string='Coordinating Ministries')
    
    total_budget = fields.Float('Total Budget', tracking=True)
    current_budget = fields.Float('Current Budget', tracking=True)
    spent_amount = fields.Float('Spent Amount', compute='_compute_spent_amount', store=True)
    budget_utilization = fields.Float('Budget Utilization (%)', compute='_compute_budget_utilization')
    
    progress = fields.Float('Progress (%)', compute='_compute_progress', store=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1', tracking=True)
    
    strategic_axis_id = fields.Many2one('government.strategic.axis', 
                                      string='Strategic Axis', 
                                      tracking=True)
    
    national_vision_id = fields.Many2one('government.national.vision', 
                                       related='strategic_axis_id.vision_id', 
                                       string='National Vision', 
                                       store=True)
    
    decision_ids = fields.Many2many('government.decision', 
                                  'project_decision_rel',
                                  'project_id', 'decision_id',
                                  string='Government Decisions')
    
    finance_law_allocations_ids = fields.Many2many('government.finance.program.allocation', 
                                                'project_finance_allocation_rel',
                                                'project_id', 'allocation_id',
                                                string='Finance Law Allocations')
    
    project_manager_id = fields.Many2one('res.users', string='Project Manager', tracking=True)
    location = fields.Char('Location', tracking=True)
    
    impact_indicators = fields.Text('Impact Indicators', tracking=True)
    notes = fields.Text('Notes')
    
    task_ids = fields.One2many('project.government.task', 'project_id', string='Tasks')
    report_ids = fields.One2many('project.government.report', 'project_id', string='Reports')
    
    color = fields.Integer('Color Index')
    active = fields.Boolean(default=True)
    
    attachment_count = fields.Integer(compute='_compute_attachment_count')
    task_count = fields.Integer(compute='_compute_task_count')
    report_count = fields.Integer(compute='_compute_report_count')
    decision_count = fields.Integer(compute='_compute_decision_count')
    
    company_id = fields.Many2one('res.company', string='Company', 
                               default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Project code must be unique!')
    ]
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for project in self:
            if project.start_date and project.end_date:
                delta = project.end_date - project.start_date
                project.duration = delta.days + 1
            else:
                project.duration = 0
    
    @api.depends('actual_start_date', 'actual_end_date')
    def _compute_actual_duration(self):
        today = fields.Date.today()
        for project in self:
            if project.actual_start_date:
                end_date = project.actual_end_date or today
                delta = end_date - project.actual_start_date
                project.actual_duration = delta.days + 1
            else:
                project.actual_duration = 0
    
    @api.depends('task_ids.amount_spent')
    def _compute_spent_amount(self):
        for project in self:
            project.spent_amount = sum(task.amount_spent for task in project.task_ids)
    
    @api.depends('spent_amount', 'current_budget')
    def _compute_budget_utilization(self):
        for project in self:
            if project.current_budget:
                project.budget_utilization = (project.spent_amount / project.current_budget) * 100
            else:
                project.budget_utilization = 0
    
    @api.depends('task_ids.progress')
    def _compute_progress(self):
        for project in self:
            if project.task_ids:
                weighted_progress = sum(task.progress for task in project.task_ids) / len(project.task_ids)
                project.progress = min(100.0, weighted_progress)
            else:
                project.progress = 0
    
    def _compute_attachment_count(self):
        for project in self:
            project.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'project.government.project'),
                ('res_id', '=', project.id)
            ])
    
    def _compute_task_count(self):
        for project in self:
            project.task_count = len(project.task_ids)
    
    def _compute_report_count(self):
        for project in self:
            project.report_count = len(project.report_ids)
    
    def _compute_decision_count(self):
        for project in self:
            project.decision_count = len(project.decision_ids)
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for project in self:
            if project.start_date and project.end_date and project.start_date > project.end_date:
                raise ValidationError(_("End date cannot be earlier than start date."))
    
    @api.onchange('strategic_axis_id')
    def _onchange_strategic_axis(self):
        if self.strategic_axis_id:
            return {'domain': {'decision_ids': [('id', 'in', self.strategic_axis_id.project_ids.mapped('decision_ids').ids)]}}
    
    @api.onchange('responsible_ministry_id')
    def _onchange_responsible_ministry(self):
        if not self.project_manager_id and self.responsible_ministry_id:
            ministry_users = self.env['res.users'].search([
                ('employee_id.department_id.name', 'ilike', self.responsible_ministry_id.name)
            ], limit=1)
            if ministry_users:
                self.project_manager_id = ministry_users[0].id
    
    # State changes
    def action_set_planned(self):
        for project in self:
            project.state = 'planned'
    
    def action_set_awaiting_decision(self):
        for project in self:
            project.state = 'awaiting_decision'
    
    def action_start_project(self):
        for project in self:
            project.state = 'in_progress'
            if not project.actual_start_date:
                project.actual_start_date = fields.Date.today()
    
    def action_hold_project(self):
        for project in self:
            project.state = 'on_hold'
    
    def action_complete_project(self):
        for project in self:
            project.state = 'completed'
            project.actual_end_date = fields.Date.today()
    
    def action_cancel_project(self):
        for project in self:
            project.state = 'cancelled'
    
    def action_reset_to_draft(self):
        for project in self:
            project.state = 'draft'
    
    # Navigation actions
    def action_view_tasks(self):
        self.ensure_one()
        return {
            'name': _('Project Tasks'),
            'view_mode': 'tree,form',
            'res_model': 'project.government.task',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id}
        }
    
    def action_view_reports(self):
        self.ensure_one()
        return {
            'name': _('Project Reports'),
            'view_mode': 'tree,form',
            'res_model': 'project.government.report',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id}
        }
    
    def action_view_decisions(self):
        self.ensure_one()
        return {
            'name': _('Government Decisions'),
            'view_mode': 'tree,form',
            'res_model': 'government.decision',
            'domain': [('id', 'in', self.decision_ids.ids)],
            'type': 'ir.actions.act_window',
        }
    
    def action_view_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', 'project.government.project'), ('res_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_res_model': 'project.government.project', 'default_res_id': self.id}
        }
    
    def action_generate_report(self):
        self.ensure_one()
        return {
            'name': _('Generate Project Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.government.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_project_id': self.id}
        }
    
    def name_get(self):
        result = []
        for project in self:
            name = project.name
            if project.code:
                name = f"[{project.code}] {name}"
            result.append((project.id, name))
        return result