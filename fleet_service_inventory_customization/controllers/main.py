# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class service_customer_information(http.Controller):

    @http.route(['/fleet_location/get_data'], type="json", auth="public")
    def get_data(self, **post):
        if post.get('model'):
            fields_with_data = {}
            rec_id = post.get('rec_id')
            fleet_location_obj = request.env['service.customer.information']
            if rec_id:
                fleet_id = fleet_location_obj.sudo().search([('id', '=', rec_id)])
                fields_with_data = {'origin':fleet_id.origin,'destination':fleet_id.destination}
            return fields_with_data
        else:
            return False
        
        
    @http.route(['/fleet_location/set_data'], type="json", auth="public")
    def set_data(self, **post):
        if post.get('miles'):
            miles = post.get('miles')
            round_miles = round(miles,1)
            rec_id = post.get('rec_id')
            fleet_location_obj = request.env['service.customer.information']
            if rec_id:
                fleet_id = fleet_location_obj.sudo().search([('id', '=', rec_id)])
                miles_new = fleet_id.sudo().write({'miles': round_miles})
            return True
        else:
            return False
        
        
    @http.route(['/fleet_location/set_data/time'], type="json", auth="public")
    def set_data_time(self, **post):
        if post.get('minut'):
            rec_id = post.get('rec_id')
            minut = post.get('minut')
            fleet_location_obj = request.env['service.customer.information']
            if rec_id:
                fleet_id = fleet_location_obj.sudo().search([('id', '=', rec_id)])
                total_time_duration = fleet_id.sudo().write({'total_time':minut})
            return True
        else:
            return False
     