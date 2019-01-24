# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



from odoo import api, fields, models, _
from odoo.exceptions import Warning,UserError,ValidationError

class ServiceMoveWizLine(models.TransientModel):
    _name = "service.move.wiz.line"

    fleet_service_id=fields.Many2one('service.move.wiz',string="Fleet Service")
    location_id= fields.Many2one('stock.location',string="Source Loaction")
    dest_location_id = fields.Many2one('stock.location',string="Destination Location")
    qty = fields.Float(string='Quantity In Truck')
    is_truck = fields.Boolean(string="Transfer ?")
    final_quantity = fields.Float(string="Quantity")

class ServiceMoveWiz(models.TransientModel):
    _name = 'service.move.wiz'

    fleet_location_ids = fields.One2many('service.move.wiz.line','fleet_service_id',string="Fleet Location")
    product_id = fields.Many2one('product.product',string="Product")
    is_truck_move = fields.Boolean(string="Check",default=False)
    required_message = fields.Char(
        string='Please Check the Transfer', default="* Ensure to select the transfer box in order to complete the transfer of parts", readonly=True)
    
    @api.onchange('fleet_location_ids')
    @api.multi
    def onchnage_truck_button(self):
        for line in self.fleet_location_ids:
            if line.final_quantity > line.qty:
                raise ValidationError(_('Value must be less than (%s)') % line.qty)

    @api.onchange('product_id')
    @api.multi
    def onchnage_inter_truck_product(self):
        truck_list = []
        stock_quants_obj = self.env['stock.quant'].search([('product_id','=',self.product_id.id)])
        for stocks in stock_quants_obj:
            if stocks.location_id.is_fleet_location:
                qty = stocks.quantity - stocks.reserved_quantity
                if qty >0 :
                    truck_list.append((0,0,{'location_id':stocks.location_id.id,'qty':qty,'final_quantity':0.0}))
                    self.fleet_location_ids = truck_list
            else:
                self.fleet_location_ids = truck_list

    #Internal Truck Transfer Move
    @api.multi
    def truck_transfer(self):
        for picking in self:
            for line in picking.fleet_location_ids:
                if line.is_truck:
                    if not line.dest_location_id:
                        raise ValidationError(_('Please select truck destination location')) 
                    move_line_list = []
                    context = self.env.context
                    active_id = context.get('active_id')
                    truck_id = self.env['stock.picking.type'].search([('name','=',"Truck Internal Transfer")])
                    company_id = self.env['res.company']._company_default_get('service.move.wiz.line')
                    stock_picking_id = self.env['stock.picking'].search([('location_id','=',line.location_id.id),
                                                                            ('state','=','assigned'),('location_dest_id','=',line.dest_location_id.id)])
                    if stock_picking_id:
                        stock_move_obj = self.env['stock.move'].create({'product_id':self.product_id.id,
                                                                           'product_uom_qty':line.final_quantity,
                                                                           'product_uom':self.product_id.uom_id.id,
                                                                           'name':self.product_id.name,
                                                                           'picking_id' : stock_picking_id.id,
                                                                           'location_id':line.location_id.id,
                                                                           'location_dest_id':line.dest_location_id.id,
                                                                           })
                        stock_move_obj.picking_id.action_confirm()
                        stock_picking_id.action_assign()
                    if not stock_picking_id:
                        move_line_list.append((0,0,{'product_id':self.product_id.id,
                                                   'product_uom_qty':line.final_quantity,
                                                   'product_uom':self.product_id.uom_id.id,
                                                   'name':self.product_id.name,
                                                   }))

                        result = self.env['stock.picking'].create({'location_id':line.location_id.id,
                                                    'location_dest_id':line.dest_location_id.id,
                                                    'picking_type_id':truck_id.id,
                                                    'company_id' : company_id.id,
                                                    'move_type':'direct',
                                                    'move_lines' : move_line_list,
                                                    'origin' : 'Inter Truck Transfer',
                                                    'is_truck_transfer':True
                                                    })
                        result.action_confirm()
                        result.action_assign()
                        wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, result.id)]})
                        wiz.process()
                        result.button_validate()

            return True
