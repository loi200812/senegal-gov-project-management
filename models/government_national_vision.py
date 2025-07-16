# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class GovernmentNationalVision(models.Model):
    _name = 'government.national.vision'
    _description = 'National Vision'
    _inherit = ['gov.qr.code.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'start_year desc'

    name = fields.Char('Vision Name', required=True, tracking=True)
    start_year = fields.Integer('Start Year', required=True, tracking=True)
    end_year = fields.Integer('End Year', required=True, tracking=True)
    description = fields.Text('Description', tracking=True)
    
    axis_ids = fields.One2many('government.strategic.axis', 'vision_id', 
                              string='Strategic Axes')
    
    active = fields.Boolean(default=True)
    attachment_ids = fields.Many2many('ir.attachment', 
                                    'vision_attachment_rel', 
                                    'vision_id', 'attachment_id', 
                                    string='Documents')
    
    president_id = fields.Many2one('res.partner', string='President', 
                                 domain=[('is_company', '=', False)])
    
    image = fields.Binary('Vision Image', attachment=True)
    url = fields.Char('External URL')
    
    axis_count = fields.Integer(compute='_compute_axis_count')
    project_count = fields.Integer(compute='_compute_project_count')
    
    company_id = fields.Many2one('res.company', string='Company', 
                               default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Vision name must be unique!'),
        ('year_check', 'check(end_year > start_year)', 'End year must be greater than start year!')
    ]
    
    @api.depends('axis_ids')
    def _compute_axis_count(self):
        for vision in self:
            vision.axis_count = len(vision.axis_ids)

    @api.depends('axis_ids.project_ids')
    def _compute_project_count(self):
        for vision in self:
            project_ids = self.env['project.government.project'].search([
                ('strategic_axis_id', 'in', vision.axis_ids.ids)
            ])
            vision.project_count = len(project_ids)

    def action_view_axes(self):
        self.ensure_one()
        return {
            'name': _('Strategic Axes'),
            'view_mode': 'tree,form',
            'res_model': 'government.strategic.axis',
            'domain': [('vision_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_vision_id': self.id}
        }

    def action_view_projects(self):
        self.ensure_one()
        project_ids = self.env['project.government.project'].search([
            ('strategic_axis_id', 'in', self.axis_ids.ids)
        ])
        return {
            'name': _('Vision Projects'),
            'view_mode': 'tree,form,kanban',
            'res_model': 'project.government.project',
            'domain': [('id', 'in', project_ids.ids)],
            'type': 'ir.actions.act_window',
        }