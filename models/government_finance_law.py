# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class GovernmentFinanceLaw(models.Model):
    _name = 'government.finance.law'
    _description = 'Finance Law'
    _inherit = ['gov.qr.code.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'year desc, id desc'

    name = fields.Char('Finance Law Name', required=True, tracking=True)
    reference = fields.Char('Reference', tracking=True)
    year = fields.Integer('Budget Year', required=True, tracking=True)
    
    type = fields.Selection([
        ('initiale', 'Initial Finance Law'),
        ('rectificative', 'Amending Finance Law')
    ], string='Type', required=True, default='initiale', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('enacted', 'Enacted')
    ], string='Status', default='draft', tracking=True)
    
    approval_date = fields.Date('Approval Date')
    enactment_date = fields.Date('Enactment Date')
    
    total_budget_allocated = fields.Float('Total Budget Allocated', 
                                       compute='_compute_total_budget', 
                                       store=True)
    
    program_allocations_ids = fields.One2many('government.finance.program.allocation', 
                                            'finance_law_id', 
                                            string='Program Allocations')
    
    document_ids = fields.Many2many('ir.attachment', 
                                  'finance_law_attachment_rel', 
                                  'finance_law_id', 'attachment_id', 
                                  string='Documents')
    
    description = fields.Text('Description')
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one('res.company', string='Company', 
                              default=lambda self: self.env.company)
    
    @api.depends('program_allocations_ids.allocated_amount')
    def _compute_total_budget(self):
        for law in self:
            law.total_budget_allocated = sum(law.program_allocations_ids.mapped('allocated_amount'))
    
    @api.constrains('year', 'type')
    def _check_unique_finance_law(self):
        for law in self:
            domain = [
                ('year', '=', law.year),
                ('type', '=', law.type),
                ('id', '!=', law.id)
            ]
            if self.search_count(domain):
                raise ValidationError(_('A finance law of this type already exists for the year %s!') % law.year)
    
    def action_propose(self):
        for law in self:
            law.state = 'proposed'
    
    def action_approve(self):
        for law in self:
            law.state = 'approved'
            law.approval_date = fields.Date.today()
    
    def action_enact(self):
        for law in self:
            law.state = 'enacted'
            law.enactment_date = fields.Date.today()
    
    def action_draft(self):
        for law in self:
            law.state = 'draft'
            
    def name_get(self):
        result = []
        for law in self:
            name = f"{law.name} ({law.year})"
            if law.reference:
                name = f"{name} [{law.reference}]"
            result.append((law.id, name))
        return result


class GovernmentFinanceProgramAllocation(models.Model):
    _name = 'government.finance.program.allocation'
    _description = 'Program Budget Allocation'
    _inherit = ['gov.qr.code.mixin']
    _order = 'sequence, id'

    name = fields.Char('Program Name', required=True)
    code = fields.Char('Program Code')
    sequence = fields.Integer('Sequence', default=10)
    
    finance_law_id = fields.Many2one('government.finance.law', string='Finance Law', 
                                   required=True, ondelete='cascade')
    
    allocated_amount = fields.Float('Allocated Amount', required=True)
    spent_amount = fields.Float('Spent Amount', compute='_compute_spent_amount')
    remaining_amount = fields.Float('Remaining Amount', compute='_compute_remaining_amount')
    
    project_ids = fields.Many2many('project.government.project', 
                                'project_finance_allocation_rel',
                                'allocation_id', 'project_id',
                                string='Funded Projects')
    
    ministry_id = fields.Many2one('government.ministry', string='Responsible Ministry')
    
    description = fields.Text('Description')
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one('res.company', string='Company', 
                              related='finance_law_id.company_id', store=True)
    
    @api.depends('project_ids.spent_amount')
    def _compute_spent_amount(self):
        for allocation in self:
            allocation.spent_amount = sum(allocation.project_ids.mapped('spent_amount'))
    
    @api.depends('allocated_amount', 'spent_amount')
    def _compute_remaining_amount(self):
        for allocation in self:
            allocation.remaining_amount = allocation.allocated_amount - allocation.spent_amount
            
    def name_get(self):
        result = []
        for allocation in self:
            name = allocation.name
            if allocation.code:
                name = f"[{allocation.code}] {name}"
            if allocation.finance_law_id:
                name = f"{name} ({allocation.finance_law_id.year})"
            result.append((allocation.id, name))
        return result