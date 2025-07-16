# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProjectGovernmentTask(models.Model):
    _name = 'project.government.task'
    _description = 'Government Project Task'
    _inherit = ['gov.qr.code.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'sequence, priority desc, id desc'

    name = fields.Char('Task Name', required=True, tracking=True)
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description')
    
    project_id = fields.Many2one('project.government.project', 
                               string='Project', 
                               required=True, 
                               ondelete='cascade', 
                               tracking=True)
    
    assigned_to_id = fields.Many2one('res.users', string='Assigned To', tracking=True)
    
    start_date = fields.Date('Start Date', tracking=True)
    deadline = fields.Date('Deadline', tracking=True)
    completion_date = fields.Date('Completion Date', tracking=True)
    
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='new', tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1', tracking=True)
    
    progress = fields.Float('Progress (%)', default=0, tracking=True)
    
    amount_planned = fields.Float('Planned Budget', tracking=True)
    amount_spent = fields.Float('Amount Spent', tracking=True)
    
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready for next stage'),
        ('blocked', 'Blocked')
    ], string='Kanban State', default='normal', tracking=True)
    
    color = fields.Integer('Color Index')
    active = fields.Boolean(default=True)
    
    documents_ids = fields.Many2many('ir.attachment', 
                                   'task_attachment_rel', 
                                   'task_id', 'attachment_id', 
                                   string='Documents')
    
    ministry_id = fields.Many2one('government.ministry', 
                               related='project_id.responsible_ministry_id', 
                               store=True, 
                               string='Ministry')
    
    parent_task_id = fields.Many2one('project.government.task', string='Parent Task')
    child_task_ids = fields.One2many('project.government.task', 'parent_task_id', string='Sub-tasks')
    child_task_count = fields.Integer(compute='_compute_child_task_count')
    
    tags = fields.Many2many('project.tags', string='Tags')
    
    company_id = fields.Many2one('res.company', 
                              related='project_id.company_id', 
                              string='Company', 
                              store=True)
    
    @api.depends('child_task_ids')
    def _compute_child_task_count(self):
        for task in self:
            task.child_task_count = len(task.child_task_ids)
    
    @api.constrains('parent_task_id')
    def _check_parent_task(self):
        for task in self:
            if task.parent_task_id:
                if task.parent_task_id == task:
                    raise ValidationError(_("A task cannot be its own parent!"))
                if task.parent_task_id.parent_task_id == task:
                    raise ValidationError(_("Circular parent/child relationship detected!"))
    
    @api.constrains('start_date', 'deadline')
    def _check_dates(self):
        for task in self:
            if task.start_date and task.deadline and task.start_date > task.deadline:
                raise ValidationError(_("Deadline cannot be earlier than start date."))
    
    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id and not self.assigned_to_id:
            self.assigned_to_id = self.project_id.project_manager_id
    
    def action_start(self):
        for task in self:
            task.state = 'in_progress'
            if not task.start_date:
                task.start_date = fields.Date.today()
    
    def action_block(self):
        for task in self:
            task.state = 'blocked'
    
    def action_done(self):
        for task in self:
            task.state = 'done'
            task.progress = 100
            task.completion_date = fields.Date.today()
            self._update_project_progress(task.project_id.id)
    
    def action_cancel(self):
        for task in self:
            task.state = 'cancelled'
    
    def action_reset(self):
        for task in self:
            task.state = 'new'
    
    def _update_project_progress(self, project_id):
        """Update project progress based on tasks completion"""
        if project_id:
            project = self.env['project.government.project'].browse(project_id)
            if project:
                # This will trigger the compute method on the project
                project._compute_progress()
    
    def action_view_subtasks(self):
        self.ensure_one()
        return {
            'name': _('Subtasks'),
            'view_mode': 'tree,form',
            'res_model': 'project.government.task',
            'domain': [('parent_task_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_parent_task_id': self.id, 'default_project_id': self.project_id.id}
        }
    
    def action_add_time_spent(self):
        self.ensure_one()
        return {
            'name': _('Add Time & Expenses'),
            'type': 'ir.actions.act_window',
            'res_model': 'government.task.timesheet.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_task_id': self.id}
        }