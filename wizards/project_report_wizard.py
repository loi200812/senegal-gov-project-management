# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime, timedelta

class ProjectGovernmentReportWizard(models.TransientModel):
    _name = 'project.government.report.wizard'
    _description = 'Government Project Report Wizard'
    
    project_id = fields.Many2one('project.government.project', string='Project', required=True)
    report_type = fields.Selection([
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('special', 'Special')
    ], string='Report Type', default='monthly', required=True)
    
    report_date = fields.Date('Report Date', default=fields.Date.context_today, required=True)
    period_start = fields.Date('Period Start', required=True)
    period_end = fields.Date('Period End', required=True)
    
    include_tasks = fields.Boolean('Include Tasks', default=True)
    include_budget = fields.Boolean('Include Budget', default=True)
    include_decisions = fields.Boolean('Include Government Decisions', default=True)
    include_challenges = fields.Boolean('Include Challenges', default=True)
    
    @api.onchange('report_type', 'report_date')
    def _onchange_report_type(self):
        if self.report_type and self.report_date:
            # Set period start and end based on report type
            date_obj = self.report_date
            if self.report_type == 'weekly':
                self.period_start = date_obj - timedelta(days=date_obj.weekday())
                self.period_end = self.period_start + timedelta(days=6)
            elif self.report_type == 'monthly':
                self.period_start = date(date_obj.year, date_obj.month, 1)
                if date_obj.month == 12:
                    self.period_end = date(date_obj.year + 1, 1, 1) - timedelta(days=1)
                else:
                    self.period_end = date(date_obj.year, date_obj.month + 1, 1) - timedelta(days=1)
            elif self.report_type == 'quarterly':
                quarter = ((date_obj.month - 1) // 3) + 1
                self.period_start = date(date_obj.year, ((quarter - 1) * 3) + 1, 1)
                if quarter == 4:
                    self.period_end = date(date_obj.year + 1, 1, 1) - timedelta(days=1)
                else:
                    self.period_end = date(date_obj.year, (quarter * 3) + 1, 1) - timedelta(days=1)
            elif self.report_type == 'annual':
                self.period_start = date(date_obj.year, 1, 1)
                self.period_end = date(date_obj.year, 12, 31)
    
    def _prepare_report_data(self):
        """Prepare data for report generation"""
        self.ensure_one()
        project = self.project_id
        
        # Basic report data
        report_data = {
            'name': f"{self.report_type.capitalize()} Report - {project.name} - {self.report_date}",
            'project_id': project.id,
            'report_date': self.report_date,
            'report_type': self.report_type,
            'period_start': self.period_start,
            'period_end': self.period_end,
            'content': '',
            'summary': f"Project status report for {project.name} covering period from {self.period_start} to {self.period_end}.",
        }
        
        # Generate report content based on selections
        content_parts = []
        
        # Project overview
        content_parts.append(f"""
        <h2>Project Overview</h2>
        <p>Project: {project.name}</p>
        <p>Status: {dict(self.env['project.government.project'].fields_get(['state'])['state']['selection'])[project.state]}</p>
        <p>Progress: {project.progress}%</p>
        <p>Responsible Ministry: {project.responsible_ministry_id.name if project.responsible_ministry_id else 'Not assigned'}</p>
        <p>Project Manager: {project.project_manager_id.name if project.project_manager_id else 'Not assigned'}</p>
        <p>Strategic Axis: {project.strategic_axis_id.name if project.strategic_axis_id else 'Not assigned'}</p>
        """)
        
        # Tasks
        if self.include_tasks:
            tasks = self.env['project.government.task'].search([
                ('project_id', '=', project.id),
                '|',
                ('start_date', '<=', self.period_end),
                ('deadline', '>=', self.period_start)
            ])
            
            if tasks:
                content_parts.append('<h2>Tasks Progress</h2><table class="table table-bordered"><thead><tr><th>Task</th><th>Status</th><th>Progress</th><th>Deadline</th><th>Assigned To</th></tr></thead><tbody>')
                for task in tasks:
                    status = dict(self.env['project.government.task'].fields_get(['state'])['state']['selection'])[task.state]
                    content_parts.append(f"""
                    <tr>
                        <td>{task.name}</td>
                        <td>{status}</td>
                        <td>{task.progress}%</td>
                        <td>{task.deadline or ''}</td>
                        <td>{task.assigned_to_id.name if task.assigned_to_id else 'Not assigned'}</td>
                    </tr>
                    """)
                content_parts.append('</tbody></table>')
        
        # Budget
        if self.include_budget:
            content_parts.append(f"""
            <h2>Budget Information</h2>
            <table class="table table-bordered">
                <tr><td>Total Budget:</td><td>{project.total_budget:,.2f}</td></tr>
                <tr><td>Current Budget:</td><td>{project.current_budget:,.2f}</td></tr>
                <tr><td>Spent Amount:</td><td>{project.spent_amount:,.2f}</td></tr>
                <tr><td>Budget Utilization:</td><td>{project.budget_utilization:.2f}%</td></tr>
            </table>
            """)
            
            if project.finance_law_allocations_ids:
                content_parts.append('<h3>Finance Law Allocations</h3><table class="table table-bordered"><thead><tr><th>Program</th><th>Allocated Amount</th></tr></thead><tbody>')
                for allocation in project.finance_law_allocations_ids:
                    content_parts.append(f"""
                    <tr>
                        <td>{allocation.name}</td>
                        <td>{allocation.allocated_amount:,.2f}</td>
                    </tr>
                    """)
                content_parts.append('</tbody></table>')
        
        # Government Decisions
        if self.include_decisions and project.decision_ids:
            content_parts.append('<h2>Government Decisions</h2><table class="table table-bordered"><thead><tr><th>Decision</th><th>Type</th><th>Date</th><th>Reference</th></tr></thead><tbody>')
            for decision in project.decision_ids:
                decision_type = dict(self.env['government.decision'].fields_get(['type'])['type']['selection'])[decision.type]
                content_parts.append(f"""
                <tr>
                    <td>{decision.name}</td>
                    <td>{decision_type}</td>
                    <td>{decision.date}</td>
                    <td>{decision.reference or ''}</td>
                </tr>
                """)
            content_parts.append('</tbody></table>')
        
        # Challenges & Recommendations
        if self.include_challenges:
            content_parts.append("""
            <h2>Challenges and Recommendations</h2>
            <p>[This section should be filled with the specific challenges faced during the reporting period and recommendations for addressing them]</p>
            
            <h2>Next Steps</h2>
            <p>[This section should outline the next steps for the project in the upcoming period]</p>
            """)
        
        report_data['content'] = ''.join(content_parts)
        return report_data
    
    def action_generate_report(self):
        """Generate a new project report"""
        self.ensure_one()
        report_data = self._prepare_report_data()
        
        # Create the report
        report = self.env['project.government.report'].create(report_data)
        
        # Open the newly created report
        return {
            'name': _('Project Report'),
            'view_mode': 'form',
            'res_model': 'project.government.report',
            'res_id': report.id,
            'type': 'ir.actions.act_window',
        }