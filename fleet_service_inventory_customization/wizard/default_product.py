# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class FleetDefaultLoadProductWiz(models.Model):
    _name = "fleet.product.wiz"
    
    fleet_product_id = fields.Many2one('fleet.product',string = "Initial Product")
    fleet_product_line_wiz = fields.One2many('fleet.product.line.wizard','fleet_product_line_wiz_id',string="Fleet Products")
    
    @api.onchange('fleet_product_id')
    def onchange_fleet_product_id(self):
        prod_list = []
        active_id = self._context['active_id']
        stock_val = self.env['stock.location'].browse([active_id])
        quant_list = []
        fleet_prod_obj = self.env['fleet.product']
        fleet_prod_id = fleet_prod_obj.search([('id','=',self.fleet_product_id.id)])
        if fleet_prod_id:
            for line in fleet_prod_id.fleet_product_line:
                quant_qty = self.env['stock.quant'].search([('product_id', '=', line.product_id.id),('location_id', '=', active_id)])
                if quant_qty:
                    prod_list.append((0,0,{'product_id':line.product_id.id,
                                           'product_qty':line.product_qty,
                                           'name':line.name,
                                           'balance_product_qty':quant_qty.quantity - quant_qty.reserved_quantity,
                                           }))
                if not quant_qty:
                    prod_list.append((0,0,{'product_id':line.product_id.id,
                                           'product_qty':line.product_qty,
                                           'name':line.name,
                                           'balance_product_qty':0.0,
                                           }))
            self.fleet_product_line_wiz = prod_list

    @api.multi
    def set_default_stock(self):
        ir_model_data = self.env['ir.model.data']
        active_id = self._context['active_id']
        move_list = []
        internal_transfer_stock_obj = self.env["stock.picking"]
        #for fetch  WH/Stock location id as a source location
        stock_location_obj = self.env["stock.location"]
        main_location_id = stock_location_obj.search([('name','=','Stock'),('location_id.name','=','WH')])
        #for fetch picking type id
        stock_picking_type_obj = self.env["stock.picking.type"]
        stock_location_type_id = ir_model_data.get_object_reference('biztech_service', 'picking_type_truck_inventory')[1]
        for move_line in self.fleet_product_line_wiz:
            move_list.append((0,0,{'product_id':move_line.product_id.id,
                                   'product_uom_qty':move_line.product_qty,
                                   'product_uom':move_line.product_id.uom_id.id,
                                   'name':move_line.product_id.name}))
        new_picking_id = internal_transfer_stock_obj.create({'location_id':main_location_id.id,
                                                            'location_dest_id':active_id,
                                                            'picking_type_id':stock_location_type_id,
                                                            'move_lines':move_list,
                                                            'origin':"Initial Truck Stock Transfer"
                                                            })
        view = self.env.ref('stock.view_immediate_transfer')
        wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, new_picking_id.id)]})
        stock_val = stock_location_obj.browse(active_id)
        stock_val.write({'is_initial_load_transfer':True})
        stock_val.write({'fleet_product_id':self.fleet_product_id.id})
#         wiz.process()
        return True
    
class FleetProductLineWiz(models.Model): 
    _name = 'fleet.product.line.wizard'
    
    fleet_product_line_wiz_id = fields.Many2one('fleet.product.wiz',string='Fleet Product Id')
    product_id = fields.Many2one('product.product',string='Product')
    name = fields.Text(string="Description")
    product_qty = fields.Float(string="Required Quantity")
    balance_product_qty = fields.Float(string="Balance Quantity")
    
    @api.multi
    @api.onchange('product_id')
    def onchange_product(self):
        prod_list = []
        active_id = self._context['active_id']
        stock_val = self.env['stock.location'].browse([active_id])
        quant_qty = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),('location_id', '=', active_id)])
        if quant_qty:
            self.balance_product_qty = quant_qty.quantity - quant_qty.reserved_quantity
