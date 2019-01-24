# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ImportWspcFile(models.TransientModel):

    _name = "import.service.wspc"

    attach_file= fields.Binary(string='Browse WSPC Report')
    filename = fields.Char(string='Filename')
    
    @api.multi
    def store_wspc_report(self):
        active_id = self._context['active_id']
        data_attach = {'name': self.filename,
                       'datas': self.attach_file,
                       'description': 'WSPC Report attachment',
                       'res_model': 'service.customer.information',
                       'res_id': active_id,
                        }
        new_id = self.env['ir.attachment'].create(data_attach)
    
