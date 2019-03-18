#-*- coding: utf-8 -*-
#Part of AppJetty. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, tools, _
from datetime import datetime
import time
from odoo.exceptions import Warning

class ServiceInventoryWorkflow(models.Model):
    _inherit = "service.inventory.workflow"
    _description = "Service Inventory Workflow"
#                     
    @api.depends('service_customer_info_id.fleet_location_id')
    def _is_product_in_truck(self):
        service_product_list = []
        initial_load_product=[]
        fleet_prod_obj = self.env['fleet.product'].search([],limit=1)
        for prod_line in fleet_prod_obj.fleet_product_line:
            initial_load_product.append(prod_line.product_id.id)
        for line in self:
            if line.service_customer_info_id.fleet_location_id:

                if line.product_id.type != 'service':
                    quant_id = self.env['stock.quant'].search([('product_id','=', line.product_id.id),
                                                               ('location_id', '=', line.service_customer_info_id.fleet_location_id.id)])
                    if line.product_id.id == quant_id.product_id.id:
                        line.truck_quantity = quant_id.quantity - quant_id.reserved_quantity
                        if line.product_uom_qty <= quant_id.quantity - quant_id.reserved_quantity:
                            line.product_in_truck = 'YES'
                        else:
                            line.product_in_truck = 'NO'
                    else:
                        line.product_in_truck = 'NO'

    product_in_truck = fields.Char(string="Loaded In Truck",compute='_is_product_in_truck',)
    truck_quantity = fields.Float(string="Quantity In Truck", store=True,compute='_is_product_in_truck')

class service_customer_information(models.Model):
    _inherit = 'service.customer.information'
    
    vehicle_id = fields.Many2one('fleet.vehicle',string="Vehicle")
    move_count = fields.Integer("Moves")
    miles = fields.Float(string="Miles")
    origin = fields.Char(compute='_get_address',string="Origin")
    destination = fields.Char(compute='_get_address',string="Destination")
    total_time = fields.Char("Time")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    fleet_location_id = fields.Many2one('stock.location', string="Fleet Location Id")

    
    @api.multi
    def write(self, vals):
        if vals.get('vehicle_id'):
            fleet_val = self.env['fleet.vehicle'].browse(vals.get('vehicle_id'))
            vals.update({'fleet_location_id':fleet_val.service_stock_id.id})
        rec=super(service_customer_information, self).write(vals)
        #list for non extra product
        initial_load_product=[]
        fleet_prod_obj = self.env['fleet.product'].search([],limit=1)
        for prod_line in fleet_prod_obj.fleet_product_line:
            initial_load_product.append(prod_line.product_id.id)
        if vals.get('fleet_location_id'):
            quant_product_list = []
            for fleet_quant in self.fleet_location_id.quant_ids:
                quant_product_list.append(fleet_quant.product_id.id)
            service_product_list = []
            always_full = False
            always_full = all([True for line in self.service_inventory_workflow if line.product_id.type == 'service'])
            for line in self.service_inventory_workflow:
                if line.product_id.type != 'service':
                    quant_id = self.env['stock.quant'].search([('product_id','=', line.product_id.id),('location_id', '=', vals.get('fleet_location_id'))])
                    if line.product_uom_qty <= quant_id.quantity - quant_id.reserved_quantity:
                        always_full = True
                    else:
                        always_full = False
                        break
            if always_full:
                self.all_service_product=True
                self.is_transfer_main_to_truck=True
            else:
                self.is_truck_already_loaded=False
                self.is_transfer_main_to_truck=False
        return rec
     
    #for get the addres value of origin and destination
    @api.depends('partner_id')
    def _get_address(self):
        for rec in self:
            company = self.env.user.company_id.partner_id
            p_add = c_add =''
            partner = rec.partner_id
            if partner.street:
                p_add+=partner.street
            if partner.street2:
                p_add+=','+partner.street2
            if partner.city:
                p_add+=','+partner.city
            if partner.state_id:
                p_add+=','+partner.state_id.name
            if partner.country_id:
                p_add+=','+partner.country_id.name
            if partner.zip:
                p_add+=','+partner.zip  
            rec.destination = p_add
            #company address
            if company.street:
                c_add+=company.street
            if company.street2:
                c_add+=','+company.street2
            if company.city:
                c_add+=','+company.city
            if company.state_id:
                c_add+=','+company.state_id.name
            if company.country_id:
                c_add+=','+company.country_id.name
            if company.zip:
                c_add+=','+company.zip
            rec.origin = c_add
            return {'origin':rec.origin,'destination':rec.destination}
            

    @api.multi
    def open_journey(self):
        company = self.env.user.company_id
        if self.partner_id:
            partner = self.partner_id
            url="http://maps.google.com/maps?saddr="
            if company.street:
                url+=company.street.replace(' ','+')
            if company.street2:
                url+='+'+company.street2.replace(' ','+')
            if company.city:
                url+='+'+company.city.replace(' ','+')
            if company.state_id:
                url+='+'+company.state_id.name.replace(' ','+')
            if company.country_id:
                url+='+'+company.country_id.name.replace(' ','+')
            if company.zip:
                url+='+'+company.zip.replace(' ','+')
            url+="&daddr="
            if partner.street:
                url+=partner.street.replace(' ','+')
            if partner.street2:
                url+='+'+partner.street2.replace(' ','+')
            if partner.city:
                url+='+'+partner.city.replace(' ','+')
            if partner.state_id:
                url+='+'+partner.state_id.name.replace(' ','+')
            if partner.country_id:
                url+='+'+partner.country_id.name.replace(' ','+')
            if partner.zip:
                url+='+'+partner.zip.replace(' ','+')  
            
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'target': 'new'
        }
        
#for add driver assign boolean field in users
        
class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'
    
    @api.multi
    @api.depends('name', 'brand_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.brand_id.name:
                name = name
            res.append((record.id, name))
        return res
    
class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    is_for_service_work = fields.Boolean(string="For Service Truck",default = False)
    service_stock_id = fields.Many2one('stock.location',string="Service Location")
    driver_user_id = fields.Many2one('res.users',string="Driver")
    technician_gruop_id = fields.Integer(string="group")
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Make", related="model_id.brand_id")
    
    @api.model
    def default_get(self,default_fields):
        res = super(fleet_vehicle, self).default_get(default_fields)
        tach_id = self.env['res.groups'].search([('name', '=', 'Technician')], limit=1)
        res['technician_gruop_id']=tach_id.id
        return res
        
    @api.model
    def create(self, vals):
        v_id = super(fleet_vehicle, self).create(vals)
        stock_obj = self.env['stock.location']
        new_st_id = stock_obj.create({'name':'Location - '+v_id.brand_id.name+'/'+v_id.model_id.name,
                                      'usage':'internal',
                                      'is_fleet_location':True
                                      })
        v_id.update({'is_for_service_work':True,'service_stock_id':new_st_id.id})
        return v_id
