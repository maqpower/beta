# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class confirmation_view(models.TransientModel):

    _name = "confirmation.view"

    @api.multi
    def stop_workorder(self):
        ir_model_data = self.env['ir.model.data']
        active_id = self._context['active_id']
        active_model = self.env['service.customer.information'].browse([active_id])
        stock_location_type_id = ir_model_data.get_object_reference('biztech_service', 'picking_type_truck_delivery')[1]
        
        active_model.end_previous()
        active_model.auto_replacement_button()
        state_obj = self.env['service.stage'].search(
            [('name', '=', 'Completed')], limit=1)
        
        for picking in active_model.picking_ids:
            if picking.picking_type_id.id==stock_location_type_id:
                if picking.state not in ['cancel','done']:
                    picking.action_assign()
                    picking.button_validate()
                    wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, picking.id)]})
                    wiz.process()
                return active_model.write({'state': 'completed', 'end_date': fields.Datetime.now(), 'stage_id': state_obj.id,'fully_complete':True})
