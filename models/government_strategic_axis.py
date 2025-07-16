# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class GovernmentStrategicAxis(models.Model):
    _name = 'government.strategic.axis'
    _description = 'Strategic Axis'
    _inherit = ['gov.qr.code.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char('Axis Name', required=True, tracking=True)
    code = fields.Char('Axis Code', tracking=True)
    description = fields.Text('Description', tracking=True)
    sequence = fields.Integer('Sequence', default=10)
    
    vision_id = fields.Many2one('government.national.vision', string='National Vision', 
                              required=True, tracking=True,
                              ondelete='cascade')
    
    project_ids = fields.One2many('project.government.project', 'strategic_axis_id', 
                                 string='Related Projects')
    
    active = fields.Boolean(default=True)
    color = fields.Integer('Color Index')
    
    ministry_ids = fields.Many2many('government.ministry', string='Ministries Involved',
                                  compute='_compute_ministry_ids', store=True)
    
    attachment_ids = fields.Many2many('ir.attachment', 
                                    'axis_attachment_rel', 
                                    'axis_id', 'attachment_id', 
                                    string='Documents')
    
    project_count = fields.Integer(compute='_compute_project_count')
    
    target_metrics = fields.Text('Target Metrics', help="Key performance indicators for this strategic axis")
    
    company_id = fields.Many2one('res.company', string='Company', 
                               default=lambda self: self.env.company)

    _sql_constraints = [
        ('vision_code_unique', 'unique(vision_id, code)', 'Axis code must be unique per vision!')
    ]
    
    @api.depends('project_ids')
    def _compute_project_count(self):
        for axis in self:
            axis.project_count = len(axis.project_ids)
    
    @api.depends('project_ids.responsible_ministry_id', 'project_ids.coordinating_ministries_ids')
    def _compute_ministry_ids(self):
        for axis in self:
            ministry_ids = self.env['government.ministry']
            for project in axis.project_ids:
                if project.responsible_ministry_id:
                    ministry_ids |= project.responsible_ministry_id
                ministry_ids |= project.coordinating_ministries_ids
            axis.ministry_ids = ministry_ids
    
    def action_view_projects(self):
        self.ensure_one()
        return {
            'name': _('Axis Projects'),
            'view_mode': 'tree,form,kanban',
            'res_model': 'project.government.project',
            'domain': [('strategic_axis_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_strategic_axis_id': self.id}
        }

    def name_get(self):
        result = []
        for axis in self:
            name = f"[{axis.vision_id.name}] {axis.name}"
            if axis.code:
                name = f"[{axis.code}] {name}"
            result.append((axis.id, name))
        return result