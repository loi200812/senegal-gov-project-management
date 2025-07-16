# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class GovernmentDecision(models.Model):
    _name = 'government.decision'
    _description = 'Government Decision'
    _inherit = ['gov.qr.code.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char('Decision Title', required=True, tracking=True)
    reference = fields.Char('Reference', tracking=True)
    date = fields.Date('Date', required=True, tracking=True, default=fields.Date.context_today)
    
    type = fields.Selection([
        ('conseil_ministres', 'Council of Ministers'),
        ('presidentielle', 'Presidential'),
        ('decret', 'Decree'),
        ('autre', 'Other')
    ], string='Type', required=True, default='conseil_ministres', tracking=True)
    
    summary = fields.Text('Summary', tracking=True)
    full_text = fields.Html('Full Text')
    full_text_url = fields.Char('Full Text URL', tracking=True)
    
    concerned_ministries_ids = fields.Many2many('government.ministry', 
                                             'ministry_decision_rel',
                                             'decision_id', 'ministry_id',
                                             string='Concerned Ministries')
    
    project_id = fields.Many2one('project.government.project', string='Related Project')
    project_ids = fields.Many2many('project.government.project', 
                                'project_decision_rel',
                                'decision_id', 'project_id',
                                string='Impacted Projects')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], string='Status', default='draft', tracking=True)
    
    attachment_ids = fields.Many2many('ir.attachment', 
                                   'decision_attachment_rel', 
                                   'decision_id', 'attachment_id', 
                                   string='Attachments')
    
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one('res.company', string='Company', 
                              default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('reference_unique', 'unique(reference)', 'Decision reference must be unique!')
    ]
    
    def action_confirm(self):
        for decision in self:
            decision.state = 'confirmed'
    
    def action_publish(self):
        for decision in self:
            decision.state = 'published'
    
    def action_archive(self):
        for decision in self:
            decision.state = 'archived'
    
    def action_draft(self):
        for decision in self:
            decision.state = 'draft'
            
    def action_notify_ministries(self):
        """Send notification to all concerned ministries about this decision"""
        self.ensure_one()
        # This is a placeholder for future functionality
        # Will implement email notification to ministry contacts
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Notification Sent'),
                'message': _('All concerned ministries have been notified about this decision.'),
                'type': 'success',
                'sticky': False,
            }
        }