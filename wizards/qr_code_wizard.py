# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import qrcode
import base64
from io import BytesIO
import json

class GovernmentQRCodeWizard(models.TransientModel):
    _name = 'gov.qr.code.wizard'
    _description = 'QR Code Generation Wizard'
    
    record_id = fields.Integer('Record ID', required=True)
    model = fields.Char('Model', required=True)
    qr_code = fields.Binary('QR Code', readonly=True)
    qr_code_url = fields.Char('QR Code URL', readonly=True)
    name = fields.Char('Record Name', readonly=True)
    model_name = fields.Char('Model Name', compute='_compute_model_name')
    
    @api.model
    def default_get(self, fields_list):
        res = super(GovernmentQRCodeWizard, self).default_get(fields_list)
        if 'record_id' in res and 'model' in res:
            record = self.env[res['model']].browse(res['record_id'])
            if record:
                res['name'] = record.name
                res['qr_code'] = record.qr_code
                res['qr_code_url'] = record.qr_code_url
        return res
    
    @api.depends('model')
    def _compute_model_name(self):
        for wizard in self:
            if wizard.model:
                model_id = self.env['ir.model'].sudo().search([('model', '=', wizard.model)], limit=1)
                wizard.model_name = model_id.name if model_id else wizard.model
            else:
                wizard.model_name = ''
    
    def action_print_qr_code(self):
        """Print the QR code as a PDF"""
        self.ensure_one()
        return self.env.ref('senegal_gov_project_management.action_report_qr_code').report_action(self)
    
    def action_download_qr_code(self):
        """Download the QR code as PNG"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=gov.qr.code.wizard&id=%s&field=qr_code&filename=qr_code.png&download=true' % self.id,
            'target': 'self',
        }
    
    def action_email_qr_code(self):
        """Send QR code by email"""
        self.ensure_one()
        template = self.env.ref('senegal_gov_project_management.email_template_qr_code')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = {
            'default_model': 'gov.qr.code.wizard',
            'default_res_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
        }
        return {
            'name': _('Send QR Code by Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }