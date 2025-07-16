# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import qrcode
import base64
from io import BytesIO

class QRCodeMixin(models.AbstractModel):
    _name = 'gov.qr.code.mixin'
    _description = 'QR Code Generation Mixin'

    qr_code = fields.Binary(string='QR Code', attachment=True, compute='_compute_qr_code', store=True)
    qr_code_url = fields.Char(string='QR Code URL', compute='_compute_qr_code_url')

    @api.depends('name')
    def _compute_qr_code(self):
        for record in self:
            if not record.id:
                record.qr_code = False
                continue
                
            qr_data = self._get_qr_data()
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            record.qr_code = base64.b64encode(buffered.getvalue())
    
    def _get_qr_data(self):
        """Return the data to be encoded in the QR code."""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        access_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
        
        data = {
            'id': self.id,
            'name': self.name,
            'model': self._name,
            'url': access_url,
        }
        
        # Add additional metadata based on the model
        if hasattr(self, 'state'):
            data['state'] = self.state
        if hasattr(self, 'date'):
            data['date'] = str(self.date)
        
        return str(data)
    
    def _compute_qr_code_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.qr_code_url = f"{base_url}/web#id={record.id}&model={record._name}&view_type=form"
    
    def action_view_qr_code(self):
        self.ensure_one()
        return {
            'name': _('QR Code'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'gov.qr.code.wizard',
            'target': 'new',
            'context': {'default_record_id': self.id, 'default_model': self._name},
        }