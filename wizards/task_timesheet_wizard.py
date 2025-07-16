# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class GovernmentTaskTimesheetWizard(models.TransientModel):
    _name = 'government.task.timesheet.wizard'
    _description = 'Task Timesheet & Expense Entry Wizard'
    
    task_id = fields.Many2one('project.government.task', string='Task', required=True)
    date = fields.Date('Date', default=fields.Date.context_today, required=True)
    hours_spent = fields.Float('Hours Spent')
    amount_spent = fields.Float('Amount Spent')
    description = fields.Text('Description', required=True)
    
    expense_type = fields.Selection([
        ('salary', 'Salary & Wages'),
        ('equipment', 'Equipment & Materials'),
        ('service', 'External Services'),
        ('travel', 'Travel & Accommodation'),
        ('other', 'Other Expenses')
    ], string='Expense Type')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def default_get(self, fields_list):
        res = super(GovernmentTaskTimesheetWizard, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            task = self.env['project.government.task'].browse(active_id)
            res['task_id'] = task.id
        return res
    
    @api.constrains('hours_spent')
    def _check_hours_spent(self):
        for record in self:
            if record.hours_spent < 0:
                raise ValidationError(_("Hours spent cannot be negative."))
    
    @api.constrains('amount_spent')
    def _check_amount_spent(self):
        for record in self:
            if record.amount_spent < 0:
                raise ValidationError(_("Amount spent cannot be negative."))
    
    def action_save(self):
        self.ensure_one()
        
        # Update task with new expenses
        task = self.task_id
        task.write({
            'amount_spent': task.amount_spent + self.amount_spent
        })
        
        # Update project's spent amount (will trigger compute method)
        task.project_id._compute_spent_amount()
        
        # Create activity for audit trail
        task.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('Expense recorded: %s') % self.amount_spent,
            note=self.description,
            user_id=self.env.user.id
        )
        
        # Link attachments to the task
        if self.attachment_ids:
            for attachment in self.attachment_ids:
                attachment.write({
                    'res_model': 'project.government.task',
                    'res_id': task.id
                })
        
        # Increase task progress if needed
        if self.hours_spent > 0 and task.state == 'in_progress' and task.progress < 100:
            # Simple logic: increment progress by a small percentage
            # This could be improved with more sophisticated calculation
            new_progress = min(task.progress + 5, 99)  # Don't auto-complete to 100%
            task.progress = new_progress
        
        return {'type': 'ir.actions.act_window_close'}