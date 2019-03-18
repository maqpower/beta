
from odoo import models, api, fields, _
import datetime
from odoo.exceptions import Warning,UserError, ValidationError
import datetime, calendar


class ServiceEquipment(models.Model):
    _name = "service.equipment"
    _description = "Service Equipment"

    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True)
    equipment_make_id = fields.Many2one(
        'service.equipment.make', string="Make", required=True)
    equipment_model_id = fields.Many2one(
        'service.equipment.model', string="Model", required=True)
    equipment_serial_number = fields.Char(string='Serial Number', required=True)
    date_installed = fields.Date(string='Date First Installed')
    hours_of_operation = fields.Date(string='As Of')
    hours = fields.Float(string="Hours Of Operation")
    no_of_days=fields.Float("Weekly Days Of Operation")
    no_of_hours=fields.Float("Daily Hours Of Operation")
    monthly_hours_of_operation=fields.Float("Monthly Hours Of Operation",compute="_get_total")
    total = fields.Float(string="Expected Yearly Service Visits", compute="_get_total")
    location=fields.Char(string="Location")
    
    @api.onchange('no_of_days','no_of_hours')
    def onchange_no_of_days(self):
        if self.no_of_days > 0.0:
            if self.no_of_days > 7:
                raise Warning(_('Days Are Not allowed More then 7'))
        if self.no_of_hours > 0.0:
            if self.no_of_hours > 24:
                raise Warning(_('Hours Are Not allowed More then 24'))
    
    @api.depends('no_of_days', 'no_of_hours')
    def _get_total(self):
        if self.no_of_days and self.no_of_hours:
            total_month_work = (self.no_of_days * self.no_of_hours)*4.3
            self.monthly_hours_of_operation = total_month_work
            if total_month_work > 0.0:
                self.total=round((2000/total_month_work))
                    
    @api.model
    def default_get(self, fields):
        res = super(ServiceEquipment, self).default_get(fields)
        if self._context.get('partner'):
            part = self._context.get('partner')
            res['partner_id'] = part
        return res

    @api.multi
    def name_get(self):
        res = []
        for eq in self:
            if eq.equipment_serial_number:
                name = eq.name + ' - ' + eq.equipment_serial_number
                res.append((eq.id, name))
        return res
