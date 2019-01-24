# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class schedule_work(models.TransientModel):

    _name = "schedule.work"
    _description = "Log an Activity"

    @api.model
    def _default_service_id(self):
        return self._context.get('active_id')

    schedule_date = fields.Datetime('Scheduled Date')
    technician_id = fields.Many2one('res.users', string="Technician")
    name = fields.Char(string="Service Workorder",
                       related="service_cutomer_id.name")
    partner_id = fields.Many2one(
        'res.partner', string="Customer", related="service_cutomer_id.partner_id")
    service_cutomer_id = fields.Many2one(
        'service.customer.information', stirng="Service Customer", default=_default_service_id)
    technician_gruop_id = fields.Integer(
        string="group", related="service_cutomer_id.technician_gruop_id")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    @api.onchange('schedule_date')
    def check_schedule_date(self):
        if self.schedule_date:
            
            today_date = fields.datetime.today()
            warnig_date = today_date.strftime('%Y-%m-%d %H:%M:%S')
            date = datetime.strptime(
                self.schedule_date, '%Y-%m-%d %H:%M:%S')
            now_plus_10 = date + timedelta(minutes = 2)
            if now_plus_10 <= today_date:
                raise ValidationError(
                    _('Schedule Date must be Today date or Greater then %s') % warnig_date)

    @api.multi
    def action_schedule_kanban(self):
        state_obj = self.env['service.stage'].search(
            [('name', '=', 'Schedule')], limit=1)
        # kanban action
        action = self.env.ref(
            'biztech_service.service_customert_info_action').read()[0]
        for log in self:
            log.service_cutomer_id.write({
                'technician': log.technician_id.id,
                'schedule_date': log.schedule_date,
                'state': 'schedule',
                'stage_id': state_obj.id,
                'is_schedule_done': True,
                'is_plan_done': False,
                'vehicle_id':log.fleet_vehicle_id.id
            })
            if not self.schedule_date:
                raise ValidationError(_('Please Enter a valid Schedule Date'))
        action['domain'] = [('sale_order_id', '=',self.service_cutomer_id.sale_order_id.id)]
        action['context'] = {'search_default_sale_order_id': self.service_cutomer_id.sale_order_id.id}
        return action
    
    @api.multi
    def action_schedule(self):
        state_obj = self.env['service.stage'].search(
            [('name', '=', 'Schedule')], limit=1)
        # kanban action
        action = self.env.ref(
            'biztech_service.action_customert_info_form_view').read()[0]
        for log in self:
            log.service_cutomer_id.write({
                'technician': log.technician_id.id,
                'schedule_date': log.schedule_date,
                'state': 'schedule',
                'stage_id': state_obj.id,
                'is_schedule_done': True,
                'is_plan_done': False,
                'vehicle_id':log.fleet_vehicle_id.id
            })
            if not self.schedule_date:
                raise ValidationError(_('Please Enter a valid Schedule Date'))
        return action

