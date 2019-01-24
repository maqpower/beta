import odoo.addons.decimal_precision as dp
from datetime import datetime
from odoo import models, api, fields, _
from odoo.exceptions import Warning,UserError, ValidationError
from odoo.tools import pycompat
import re
import json

regex='(?!^\d+$)^.+$'

class service_stage(models.Model):
    _name = 'service.stage'
    _order = "id"

    name = fields.Char(string="Name")

    @api.multi
    def write(self, vals):
        if vals['name']:
            raise UserError(
                _('You Can Not Change The Stage Name Of Service Work Order'))
            
class ServiceCustomerInformation(models.Model):
    _name = "service.customer.information"
    _description = "Service Customer Information"
    _inherit = ['mail.thread', 'mail.activity.mixin',
                'utm.mixin', 'format.address.mixin']
    _order = 'schedule_date'

    is_plan_done = fields.Boolean(string="Is Plan Done",default=False)
    is_schedule_done = fields.Boolean(string="Is Schedule Done",default=False)
    is_in_progress_done = fields.Boolean(string="Is In Progress Done",default=False)
    is_complete = fields.Boolean(string="Is Complete",default=False)
    edit_after_start = fields.Boolean(string='Edit after Start',default=False)
    fully_complete = fields.Boolean(string="Fully Complete",default=False)
    is_auto_replacement = fields.Boolean(string="Auto Replacement",default=False)

    @api.multi
    def send_workorder_by_email(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('biztech_service', 'email_template_service_workorder_new')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'service.customer.information',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
          
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def default_get(self, fields):
        rec = super(ServiceCustomerInformation, self).default_get(fields)
        if not self.stage_id:
            state_obj = self.env['service.stage'].search(
                [('name', '=', 'Plan')], limit=1)
            if state_obj:
                rec.update({'stage_id': state_obj.id})
        return rec

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        state = self.env['service.stage'].search([])
        return state

    @api.multi
    def write(self, vals):
        res = super(ServiceCustomerInformation, self).write(vals)
        plan_stage_id = self.env['service.stage'].search(
            [('name', '=', 'Plan')], limit=1)
        state_obj = self.env['service.stage'].search(
            [('name', '=', 'Completed')], limit=1)
        schedule_id = self.env['service.stage'].search(
            [('name', '=', 'Schedule')], limit=1)
        in_progress_id = self.env['service.stage'].search(
            [('name', '=', 'In Progress')], limit=1)
        if vals.get('stage_id') == schedule_id.id or vals.get('stage_id') == in_progress_id.id or vals.get('stage_id') == state_obj.id or vals.get('stage_id') == 1:
            if not self.technician:
                raise UserError(
                    _('Can not Move plan Service without technician'))
            if not self.time_line_ids and vals.get('is_schedule_done') == False:
                raise UserError(
                    _('Can not Move Schedule Service before start'))

            if self.is_schedule_done == True and self.is_plan_done == False and not self.time_line_ids:
                if self.is_schedule_done == True and self.is_plan_done == False:
                    pass
                else:
                    raise UserError(
                        _('Can not Move Schedule Service before start'))

            if self.is_in_progress_done == True:
                if vals.get('is_in_progress_done') == True:
                    pass
                else:
                    raise UserError(
                        _('Can not Move the service while it is continue'))
        if self.end_date:
            if vals.get('stage_id') == plan_stage_id.id or vals.get('stage_id') == schedule_id.id or vals.get('stage_id') == in_progress_id.id:
                raise UserError(_('Service will not move after Completion'))

    name = fields.Char(string='Work Order Number',
                       default=lambda self: _('New'), index=True, copy=False)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True)
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address')
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Service Address')
    
    customer_contact_ids = fields.Char(string="Contact Name")
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms')
    service_type = fields.Selection([
        ('repair', 'Repair'),
        ('troubleshoot', 'Troubleshoot'),
        ('start_up', 'Start Up'),
        ('minor_pm', 'Minor PM'),
        ('major_pm', 'Major PM'),
        ('elite_care', 'Elite Care')
    ], string="Service Type", store=True)
    po_number = fields.Char('PO Number')

    # --- for equipment information ---
    equipment_id = fields.Many2one('service.equipment', string="Equipment")
    equipment_make_id = fields.Many2one(
        'service.equipment.make', string="Make", related="equipment_id.equipment_make_id")
    equipment_model_id = fields.Many2one(
        'service.equipment.model', string="Model", related="equipment_id.equipment_model_id")
    equipment_serial_number = fields.Char(
        'Serial Number', related="equipment_id.equipment_serial_number")
    equipment_date_installed = fields.Date(
        'Date First Installed', related="equipment_id.date_installed")
    year_installed = fields.Char('Year Installed (If known)')
    equipment_compressor = fields.Text('Compressor')
    equipment_location = fields.Text('Location')

    @api.onchange('equipment_compressor', 'equipment_location')
    def _onchange_equipment_location(self):
        if self.equipment_compressor:
            if not re.match(regex,self.equipment_compressor):
                raise Warning(_('Number is not allowed in Compressor'))
        if self.equipment_location:
            if not re.match(regex,self.equipment_location):
                raise Warning(_('Number is not allowed in Location'))

    # --- for Scheduling Information ---
    user_id = fields.Many2one('res.users', string='Technician Assigned')
    no_of_service_units = fields.Integer(
        'Number of Service Units', default=1, required=True)
    date_service_scheduled = fields.Date('Date Service Scheduled')
    date_service_scheduled_success= fields.Date('Date Service Scheduled')
    date_service_performed = fields.Date('Date Service Performed')
    date_service_performed_success= fields.Date('Date Service Performed')

    @api.onchange('date_service_performed')
    def _onchange_date_service_performed(self):
        if self.date_service_performed:
            self.date_service_performed_success = self.date_service_performed

    @api.onchange('date_service_performed_success')
    def _onchange_date_service_performed_success(self):
        if self.date_service_performed_success:
            self.date_service_performed = self.date_service_performed_success

    work_details = fields.Text('Work to be Performed')
    
    @api.onchange('work_details')
    def _onchange_work_detail(self):
        if self.work_details:
            if not re.match(regex,self.work_details):
                raise Warning(_('Number is not allowed in Work to be Performed'))

    # --- for inventory related workflow ---
    conformation_usage = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Confirm Usage", store=True, default='no')
    service_inventory_workflow = fields.One2many(
        'service.inventory.workflow', 'service_customer_info_id', string="Service Inventory Workflow")

    # --- for service related data ---
    is_all_service_fields_true = fields.Boolean(
        'Is all Service Related Data fields are true')
    total_run_hours = fields.Float(
        'Total Run Hours', help="Hours the compressor unit has operated.")
    total_loaded_hours = fields.Float('Total Loaded Hours')
    loaded_pressure = fields.Float('Loaded Pressure')
    unloaded_pressure = fields.Float('Unloaded Pressure')
    ambient_temperature = fields.Float(
        'Ambient Temperature', help="In degrees Fahrengheit")
    service_location = fields.Selection([
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
    ], string="Location", store=True)
    package_discharge_temperature = fields.Float(
        'Package Discharge Temperature')
    injection_temperature = fields.Float('Injection Temperature')
    airend_discharge_tempreature = fields.Float('Airend Discharge Temperature')
    
    @api.onchange('total_run_hours', 'total_loaded_hours', 'loaded_pressure', 'unloaded_pressure', 'ambient_temperature', 'service_location', 'package_discharge_temperature', 'injection_temperature', 'airend_discharge_tempreature')
    def _onchange_service_fields(self):
        if self.total_run_hours and self.total_loaded_hours and self.loaded_pressure and self.unloaded_pressure and self.ambient_temperature and self.service_location in ('indoor', 'outdoor') and self.package_discharge_temperature and self.injection_temperature and self.airend_discharge_tempreature:
            self.is_all_service_fields_true = True
        else:
            self.is_all_service_fields_true = False

    # --- for visual inspection---
    is_all_visual_inspection_fields_true = fields.Boolean(
        'Is all Visual Inspection fields are true')
    oil_lines_inspection = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Oil Lines Visual Inspection", store=True, default='no')
    
    air_lines_inspection = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Air Lines Visual Inspection", store=True, default='no')
    control_component_inspection = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Control Components Visual Inspection", store=True, default='no')
    check_oil_discharge_temperature = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Check Oil Discharge Temperature", store=True, default='no')

    cooler_oil_temperature_inlet_and_outlet = fields.Float(
        'Cooler Oil Temperature - Inlet & Outlet')
    
    cooler_air_temperature_inlet_and_outlet = fields.Float(
        'Cooler Air Temperature - Inlet & Outlet')

    check_oil_level = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Check Oil Level", store=True, default='no')
    check_oil_or_water_separator = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Check Oil/Water Separator", store=True, default='no')
    check_air_drier = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Check Air Drier", store=True, default='no')
    check_air_line_filters = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Check All Line Filters", store=True, default='no')
    check_all_system_drain_lines = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], string="Check All System Drain Lines", store=True, default='no')

    @api.onchange('oil_lines_inspection', 'air_lines_inspection', 'control_component_inspection', 'check_oil_discharge_temperature', 'cooler_oil_temperature_inlet_and_outlet', 'cooler_air_temperature_inlet_and_outlet', 'check_oil_level', 'check_oil_or_water_separator', 'check_air_drier', 'check_air_line_filters', 'check_all_system_drain_lines')
    def _onchange_visual_inspections_fields(self):
        if self.oil_lines_inspection == 'yes' and self.air_lines_inspection == 'yes' and self.control_component_inspection == 'yes' and self.check_oil_discharge_temperature == 'yes' and self.check_oil_level == 'yes' and self.check_oil_or_water_separator == 'yes' and self.check_air_drier == 'yes' and self.check_air_line_filters == 'yes' and self.check_all_system_drain_lines == 'yes' and self.cooler_oil_temperature_inlet_and_outlet and self.cooler_air_temperature_inlet_and_outlet:
            self.is_all_visual_inspection_fields_true = True
        else:
            self.is_all_visual_inspection_fields_true = False

    # --- for electrical ---
    is_all_electrical_fields_are_true = fields.Boolean(
        'Is all Electrical fields are true')
    ele_volts_l1_l2 = fields.Float('Volts L1-L2')
    ele_volts_l2_l3 = fields.Float('Volts L2-L3')
    ele_volts_l1_l3 = fields.Float('Volts L1-L3')

    ele_l1 = fields.Float('L1')
    ele_l2 = fields.Float('L2')
    ele_l3 = fields.Float('L3')

    ele_cv1 = fields.Float('CV1')
    ele_cv2 = fields.Float('CV2')

    ele_amps_fla_l1 = fields.Float('AMPS FLA L1')
    ele_amps_fla_l2 = fields.Float('AMPS FLA L2')
    ele_amps_fla_l3 = fields.Float('AMPS FLA L3')

    ele_ula_l1 = fields.Float('ULA L1')
    ele_ula_l2 = fields.Float('ULA L2')
    ele_ula_l3 = fields.Float('ULA L3')

    @api.onchange('ele_volts_l1_l2', 'ele_volts_l2_l3', 'ele_volts_l1_l3', 'ele_l1', 'ele_l2', 'ele_l3', 'ele_cv1', 'ele_cv1', 'ele_amps_fla_l2', 'ele_amps_fla_l3', 'ele_ula_l1', 'ele_ula_l2', 'ele_ula_l3')
    def _onchange_electrical_fields(self):
        if self.ele_volts_l1_l2 and self.ele_volts_l2_l3 and self.ele_volts_l1_l3 and self.ele_l1 and self.ele_l2 and self.ele_l3 and self.ele_cv1 and self.ele_amps_fla_l1 and self.ele_amps_fla_l2 and self.ele_amps_fla_l3 and self.ele_ula_l1 and self.ele_ula_l2 and self.ele_ula_l3:
            self.is_all_electrical_fields_are_true = True
        else:
            self.is_all_electrical_fields_are_true = False

    # --- for service wrap up ---
    is_all_wrap_up_fields_true = fields.Boolean(
        "Is all Service Wrap Up fields are true")
    recommendations = fields.Text('Recommendations')
    next_schedule_visit = fields.Date('Next Suggested Scheduled Visit')
    next_schedule_visit_success = fields.Date(
        'Next Suggested Scheduled Visit')  # for display purpose only

    @api.onchange('next_schedule_visit')
    def _onchange_next_schedule_visit(self):
        if self.next_schedule_visit:
            self.next_schedule_visit_success = self.next_schedule_visit

    @api.onchange('next_schedule_visit_success')
    def _onchange_next_schedule_visit_success(self):
        if self.next_schedule_visit_success:
            self.next_schedule_visit = self.next_schedule_visit_success

    @api.onchange('recommendations', 'next_schedule_visit')
    def _onchange_service_wrap_up_fields(self):
        if self.recommendations:
            if not re.match(regex,self.recommendations):
                raise Warning(_('Number is not allowed in Recommendations'))
        if self.recommendations and self.next_schedule_visit:
            self.is_all_wrap_up_fields_true = True
        else:
            self.is_all_wrap_up_fields_true = False

    #-----for state----
    state = fields.Selection([('plan', 'Plan'),
                              ('schedule', 'Schedule'),
                              ('in_progress', 'In Progress'),
                              ('completed', 'Completed')],
                             string='Status', required=True, readonly=True, index=True, copy=False, default='plan')

    color = fields.Integer('Color Index', default=0)
    end_date = fields.Datetime("Finish Date")
    schedule_date = fields.Datetime("Schedule Date")
    technician = fields.Many2one('res.users', string="Technician")
    demo_time = fields.Float("Demo time")
#     work_schedule_ids = fields.One2many("work.schedule.line",'service_work_id',string = "Work Schedule Line")

    # new code
    time_line_ids = fields.One2many(
        'customer.workcenter.productivity', 'customer_workcenter_id', 'Time Logs')
#     total_duration = fields.Float('Real Duration', compute='_compute_duration',store=True)
    total_duration = fields.Float(
        'Real Duration', compute='_compute_total_duration', store=True, readonly=True)
    count_duration = fields.Float("Count Duration")
    is_user_working = fields.Boolean(
        'Is the Current User Working', compute='_compute_is_user_working',
        help="Technical field indicating whether the current user is working.")
    stage_id = fields.Many2one(
        'service.stage', string='Stage', group_expand='_read_group_stage_ids')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get(
        'currency.rate.update.service'))
    total_labor = fields.Float(
        string='Total Labor', compute="_get_total_labor")
    technician_gruop_id = fields.Integer(
        string="group", compute='get_technician_gruops_id')
    signature_image = fields.Binary("Customer Signature")

    required_field_message = fields.Char(
        string='Required Fields Not Completed', default="* Required Fields Not completed", readonly=True)
    is_order_valid_to_complete = fields.Boolean(
        'Is this Order valid to Complete')

    @api.onchange('is_all_service_fields_true', 'is_all_visual_inspection_fields_true', 'is_all_electrical_fields_are_true', 'is_all_wrap_up_fields_true')
    def _onchange_required_tab_fields(self):
        if self.is_all_service_fields_true and self.is_all_visual_inspection_fields_true and self.is_all_electrical_fields_are_true and self.is_all_wrap_up_fields_true:
            self.is_order_valid_to_complete = True
        else:
            self.is_order_valid_to_complete = False

    def show_warning_complete(self):
        raise Warning(_('You cannot complete order without filling following details. \n1. Service Related Data Gathering \n2. Visual Inspection \n3. Electrical \n4. Service Wrap Up'))
    
    #for default load inventory & delivery smart button
    is_transfer_main_to_truck = fields.Boolean(string="Transfer Main To Truck", default=False)
    is_transfer_truck_to_custo = fields.Boolean(string="Transfer Truck To Customer", default=False)
    picking_ids = fields.One2many('stock.picking', 'service_id', string='Pickings')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    delivery_count_technician = fields.Integer(string='Delivery Order for Technician', compute='_compute_outgoing_picking')
    is_new_product = fields.Boolean(string="New Product Found", default=False,compute="get_product_status")
    is_product_loaded=fields.Boolean(string="Additional Products Loaded in Truck?",default=False,compute="get_product_status")
    is_truck_already_loaded=fields.Boolean(string='Truck Is Allready Loaded',default=False,compute="get_product_status")
    is_extra_already_loaded=fields.Boolean(string='Extra Is Allready Loaded',default=False,compute="get_product_status")
    all_service_product=fields.Boolean(string="All service Product",default=False)
    truck_product_available=fields.Boolean(string="Truck Product Available",default=False,compute="get_product_status")

    @api.one
    def _kanban_dashboard(self):
        self.count_additional_parts = json.dumps(self.get_count_additional_parts())

    count_additional_parts = fields.Text(compute='_kanban_dashboard')

    @api.depends('service_inventory_workflow')
    def get_count_additional_parts(self):
        self.count_additional_parts = json.dumps(False)
        initial_load_product=[]
        additional_load_product=[]
        fleet_prod_obj = self.env['fleet.product'].search([],limit=1)
        for prod_line in fleet_prod_obj.fleet_product_line:
            initial_load_product.append(prod_line.product_id.id)
        for service in self:
            for line in service.service_inventory_workflow:
                if line.product_id.type != 'service':
                    if line.product_id.id not in initial_load_product:
                        additional_load_product.append(line.product_id.id)
        info = {'extra_count': len(additional_load_product)}
        return info
    
    @api.depends('service_inventory_workflow')
    def get_product_status(self):
        initial_load_product=[]
        
        fleet_prod_obj = self.env['fleet.product'].search([],limit=1)
        for prod_line in fleet_prod_obj.fleet_product_line:
            initial_load_product.append(prod_line.product_id.id)
        for service in self:
            service.is_product_loaded=True
            for line in service.service_inventory_workflow:
                if line.product_id.type != 'service':
                    quant_id = self.env['stock.quant'].search([('product_id','=', line.product_id.id),('location_id', '=',service.fleet_location_id.id)])
                    if line.product_id.id not in initial_load_product:
                        service.is_new_product=True
                        if line.product_uom_qty > quant_id.quantity - quant_id.reserved_quantity:
                            service.is_product_loaded=False
                            service.is_extra_already_loaded=False
                        else:
                            service.is_extra_already_loaded=True
                    else:
                        service.truck_product_available=True
                        if line.product_uom_qty <= quant_id.quantity - quant_id.reserved_quantity:
                            service.is_truck_already_loaded=True
                        else:
                            service.is_truck_already_loaded=False
                            break

    @api.multi
    def not_initial_item(self):
        return True
     
    @api.multi
    def extra_item_loaded(self):
        return True

    @api.multi
    def not_load(self):
        return True
    
    @api.multi
    def loaded(self):
        return True
    
    @api.depends('picking_ids')
    def _compute_outgoing_picking(self):
        ir_model_data = self.env['ir.model.data']
        do_pick_list = []
        for service in self:
            for pick_id in service.picking_ids:
                stock_location_type_id = ir_model_data.get_object_reference('biztech_service', 'picking_type_truck_delivery')[1]
                if pick_id.picking_type_id.id == stock_location_type_id:
                    do_pick_list.append(pick_id)
                    service.delivery_count_technician = len(do_pick_list)
    
    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for service in self:
            service.delivery_count = len(service.picking_ids)
            
    @api.multi
    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action
    
    @api.multi
    def action_view_delivery_outgoing(self):
        ir_model_data = self.env['ir.model.data']
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        do_pick_list = []
        for pick_id in self.picking_ids:
            stock_location_type_id = ir_model_data.get_object_reference('biztech_service', 'picking_type_truck_delivery')[1]
            if pick_id.picking_type_id.id == stock_location_type_id:
                do_pick_list.append(pick_id.id)
        if len(do_pick_list) > 1:
            action['domain'] = [('id', 'in', do_pick_list)]
        else:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pick_id.id
        return action

    #in technician field get only technician users
    @api.one
    def get_technician_gruops_id(self):
        for rec in self:
            tach_id = self.env['res.groups'].search(
                [('name', '=', 'Technician')], limit=1)
            self.technician_gruop_id = tach_id

    @api.depends('total_duration')
    def _get_total_labor(self):
        for rec in self:
            rec.total_labor = (rec.total_duration/60)

    def _compute_is_user_working(self):
        """ Checks whether the current user is working """
        for order in self:
            if order.time_line_ids.filtered(lambda x: (x.technician_id.id == order.technician.id) and (not x.date_end)):
                order.is_user_working = True
            else:
                order.is_user_working = False

    @api.one
    @api.depends('time_line_ids.duration_line')
    def _compute_total_duration(self):
        total = 0.0
        for rec in self:
            total = sum(self.time_line_ids.mapped('duration_line'))
            rec.total_duration = total

    def pause_workorder(self):
        self.end_previous()
        return True

    @api.multi
    def end_previous(self, doall=False):
        """
        @param: doall:  This will close all open time lines on the open work orders when doall = True, otherwise
        only the one of the current user
        """
        # TDE CLEANME
        timeline_obj = self.env['customer.workcenter.productivity']
        domain = [('customer_workcenter_id', 'in', self.ids),
                  ('date_end', '=', False)]
        if not doall:
            domain.append(('technician_id', '=', self.technician.id))
        not_productive_timelines = timeline_obj.browse()

        for timeline in timeline_obj.search(domain, limit=None if doall else 1):
            wo = timeline.customer_workcenter_id
#             maxdate = fields.Datetime.from_string(timeline.date_start) + relativedelta(minutes=wo.total_duration)
            enddate = datetime.now()
#             if maxdate > enddate:
#                 timeline.write({'date_end': enddate})
#             else:
            timeline.write({'date_end': enddate})
            not_productive_timelines = timeline.write({'date_end': enddate})
            self.is_complete = True
            self.is_in_progress_done = False
        return True
    
    @api.multi
    def restart_workorder(self):
        timeline = self.env['customer.workcenter.productivity']
        for workorder in self:
            timeline.create({
                'customer_workcenter_id': workorder.id,
                'date_start': datetime.now(),
                'description': _('Time Tracking: ') + self.technician.name,
                'technician_id': self.technician.id,
            })
            state_obj = self.env['service.stage'].search(
                [('name', '=', 'In Progress')], limit=1)
        return self.write({'state': 'in_progress', 'stage_id': state_obj.id, 'is_in_progress_done': True,
                           })

    @api.multi
    def start_workorder(self):
        if self.is_transfer_main_to_truck == False:
            raise Warning(_('Please Load Products from Request for Products button before start Service Work Order'))
        state_obj = self.env['service.stage'].search([('name', '=', 'In Progress')], limit=1)
        ir_model_data = self.env['ir.model.data']
        timeline = self.env['customer.workcenter.productivity']
        stock_picking_type_obj = self.env["stock.picking.type"]
        delivery_transfer_stock_obj = self.env['stock.picking']
        move_list = []
        for workorder in self:
            workorder.ensure_one()
            if workorder.picking_ids:
                for pick_id in workorder.picking_ids:
                    if pick_id.state not in ['done','cancel']:
                        raise Warning(_('Waiting for Inventory Transfer'))
                    else:
                        for move_line in workorder.service_inventory_workflow:
                            truck_location_quant = self.env['stock.quant'].search([('location_id','=',self.fleet_location_id.id),('product_id','=',move_line.product_id.id)])
                            if truck_location_quant:
                                stock_location_type_id = ir_model_data.get_object_reference('biztech_service', 'picking_type_truck_delivery')[1]
                                # if truck_location_quant.reserved_quantity != 0.0:
                                #     truck_location_quant.reserved_quantity -= move_line.product_uom_qty
                                move_list.append((0,0,{'product_id':move_line.product_id.id,
                                                       'product_uom_qty':move_line.product_uom_qty,
                                                       'product_uom':move_line.product_uom.id,
                                                       'name':move_line.product_id.name}))
                            else:
                                if move_line.product_id.type == "service":
                                    move_list.append((0,0,{'product_id':move_line.product_id.id,
                                                           'product_uom_qty':move_line.product_uom_qty,
                                                           'product_uom':move_line.product_uom.id,
                                                           'name':move_line.product_id.name}))
                    new_picking_id = delivery_transfer_stock_obj.create({'partner_id':workorder.partner_id.id,
                                                                         'sale_id':workorder.sale_order_id.id,
                                                                         'origin':workorder.name,
                                                                         'location_id':workorder.fleet_location_id.id,
                                                                         'location_dest_id':workorder.partner_id.property_stock_customer.id,
                                                                         'picking_type_id':stock_location_type_id,
                                                                         'move_lines':move_list,
                                                                         'service_id':workorder.id,
                                                                        })
                    new_picking_id.action_assign()
                    view = self.env.ref('stock.view_immediate_transfer')
                    wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, new_picking_id.id)]})
                    timeline.create({
                        'customer_workcenter_id': workorder.id,
                        'date_start': datetime.now(),
                        'description': _('Time Tracking: ') + self.technician.name,
                        'technician_id': self.technician.id,
                    })
                return self.write({'state': 'in_progress', 'is_transfer_truck_to_custo':True,'stage_id': state_obj.id, 'is_in_progress_done': True,'edit_after_start':True
                                   })
            else:
                stock_location_type_id = ir_model_data.get_object_reference('biztech_service', 'picking_type_truck_delivery')[1]
                for move_line in workorder.service_inventory_workflow:
                    truck_location_quant = self.env['stock.quant'].search([('location_id','=',self.fleet_location_id.id),('product_id','=',move_line.product_id.id)])
                    # if truck_location_quant.reserved_quantity != 0.0:
                    #     truck_location_quant.reserved_quantity -= move_line.product_uom_qty
                    move_list.append((0,0,{'product_id':move_line.product_id.id,
                                           'product_uom_qty':move_line.product_uom_qty,
                                           'product_uom':move_line.product_uom.id,
                                           'name':move_line.product_id.name}))
            new_picking_id = delivery_transfer_stock_obj.create({'partner_id':workorder.partner_id.id,
                                                                 'sale_id':workorder.sale_order_id.id,
                                                                 'origin':workorder.name,
                                                                 'location_id':workorder.fleet_location_id.id,
                                                                 'location_dest_id':workorder.partner_id.property_stock_customer.id,
                                                                 'picking_type_id':stock_location_type_id,
                                                                 'move_lines':move_list,
                                                                 'service_id':workorder.id,
                                                                })
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, new_picking_id.id)]})
            new_picking_id.action_assign()
            timeline.create({
                'customer_workcenter_id': workorder.id,
                'date_start': datetime.now(),
                'description': _('Time Tracking: ') + self.technician.name,
                'technician_id': self.technician.id,
            })
            return self.write({'state': 'in_progress', 'is_transfer_truck_to_custo':True,'stage_id': state_obj.id, 'is_in_progress_done': True,'edit_after_start':True
                               })


    @api.multi
    def auto_replacement_button(self):
        initial_product_list=[]
        move_line_auto = []
        if self.vehicle_id.service_stock_id.is_initial_load_transfer:
            for fleet_prod in self.fleet_location_id.fleet_product_id.fleet_product_line:
                    for intial_prod in fleet_prod.product_id.ids:
                        initial_product_list.append(intial_prod)
            for service_product_line in self.service_inventory_workflow:
                if service_product_line.product_id.id in initial_product_list:
                    stock_quant_location = self.env['stock.quant'].search([('location_id','=',self.fleet_location_id.id),
                                                                            ('product_id','=',service_product_line.product_id.id)])
                    truck_id = self.env['stock.picking.type'].search([('name','=',"Auto Replacement Transfer")])
                    company_id = self.env['res.company']._company_default_get('service.customer.information')
                    stock_location_id = self.env['stock.location'].search([('name','=','Stock'),('location_id.name','=','WH')])
                    stock_picking_obj = self.env['stock.picking']
                    stock_picking_id = stock_picking_obj.search([('location_id','=',stock_location_id.id),('picking_type_id','=',truck_id.id),
                                                                            ('location_dest_id','=',self.fleet_location_id.id),
                                                                            ('state','=','assigned')])
                    stock_move_obj = self.env['stock.move']
                    for stocks in stock_quant_location:
                        total_quantity_count = stocks.quantity - stocks.reserved_quantity
                        final_quantity = stocks.initial_qty_relate - total_quantity_count
                        if total_quantity_count<stocks.re_order_qty:
                                if stock_picking_id:
                                    self.env['stock.move'].create({'product_id':service_product_line.product_id.id,
                                                                                   'product_uom_qty':service_product_line.product_uom_qty,
                                                                                   'product_uom':service_product_line.product_id.uom_id.id,
                                                                                   'name':service_product_line.product_id.name,
                                                                                   'picking_id' : stock_picking_id.id,
                                                                                   'location_id':stock_location_id.id,
                                                                                   'location_dest_id':self.fleet_location_id.id,
                                                                                   })
                                    stock_move_obj.picking_id.action_confirm()

                                    stock_picking_id.action_assign()
                                else:
                                    move_line_auto.append((0,0,{'product_id':service_product_line.product_id.id,
                                                           'product_uom_qty':final_quantity,
                                                           'product_uom':service_product_line.product_id.uom_id.id,
                                                           'name':service_product_line.product_id.name,
                                                           }))
                                    result = self.env['stock.picking'].create({'location_id':stock_location_id.id,
                                        'location_dest_id':self.fleet_location_id.id,
                                        'picking_type_id':truck_id.id,
                                        'company_id' : company_id.id,
                                        'move_type':'direct',
                                        'move_lines' : move_line_auto,
                                        'service_id' : service_product_line.service_customer_info_id.id,
                                        'origin' : 'Auto Replacement Truck Transfer',
                                        'is_truck_transfer':True
                                        })
                                    result.action_confirm()
                                    result.action_assign()
            return self.write({'is_auto_replacement': True})

    @api.multi
    def load_product_to_fleet(self):
        if not self.equipment_id:
            raise ValidationError(
                    _('Please Select Equipments First'))
        if self.equipment_id:
            ir_model_data = self.env['ir.model.data']
            #for fetch picking type id
            move_list = []
            internal_transfer_stock_obj = self.env["stock.picking"]
            #for fetch  WH/Stock location id as a source location
            stock_location_obj = self.env["stock.location"]
            main_location_id = stock_location_obj.search([('name','=','Stock'),('location_id.name','=','WH')])
            #for fetch picking type id
            stock_picking_type_obj = self.env["stock.picking.type"]
            stock_location_type_id = ir_model_data.get_object_reference('biztech_service', 'picking_type_truck_inventory')[1]
            quant_product_list = []
            #make the list of current stock product of current fleet location 
            for fleet_quant in self.fleet_location_id.quant_ids:
                quant_product_list.append(fleet_quant.product_id.id)
            service_product_list= []
            for service_prod in self.service_inventory_workflow:
                if service_prod.product_id.type=='service':
                    service_product_list.append(service_prod.product_id.id)
            for swo_line in self.service_inventory_workflow:
                quant_id = self.env['stock.quant'].search([('location_id','=',main_location_id.id),('product_id','=',swo_line.product_id.id)],limit=1)
                truck_location_quant = self.env['stock.quant'].search([('location_id','=',self.fleet_location_id.id),('product_id','=',swo_line.product_id.id)])
                if quant_id:
                    if truck_location_quant:
                        if swo_line.product_id.id == quant_id.product_id.id:
                            if (truck_location_quant.quantity - truck_location_quant.reserved_quantity) < swo_line.product_uom_qty:
                                if quant_id.quantity - quant_id.reserved_quantity < swo_line.product_uom_qty:
                                    raise Warning(_('Not enough Product Quantity in main stock.Please Contact Inventory Manager Of %s')%(swo_line.product_id.name,))
                                diff_qty = swo_line.product_uom_qty - (truck_location_quant.quantity - truck_location_quant.reserved_quantity)
                                move_list.append((0,0,{'product_id':swo_line.product_id.id,
                                                       'product_uom_qty':diff_qty,
                                                       'product_uom':swo_line.product_uom.id,
                                                       'name':swo_line.product_id.name}))
                            #     truck_location_quant.reserved_quantity += (truck_location_quant.quantity - truck_location_quant.reserved_quantity)+diff_qty
                            # else:
                            #     truck_location_quant.reserved_quantity += swo_line.product_uom_qty
                    else:
                        new_product = []
                        if swo_line.product_id.id not in quant_product_list:
                            
                            if quant_id.quantity - quant_id.reserved_quantity < swo_line.product_uom_qty:
                                raise Warning(_('Not enough Product Quantity in main stock.Please Contact Inventory Manager Of %s')%(swo_line.product_id.name,))
                            else:
                                new_product.append(swo_line.product_id.id)
                                move_list.append((0,0,{'product_id':swo_line.product_id.id,
                                                       'product_uom_qty':swo_line.product_uom_qty,
                                                       'product_uom':swo_line.product_uom.id,
                                                       'name':swo_line.product_id.name}))
                else:
                    if swo_line.product_id.id in service_product_list:
                        pass
                    else:
                        raise Warning(_('Not enough Product Quantity in main stock.Please Contact Inventory Manager Of %s')%(swo_line.product_id.name,))
            if move_list:
                new_picking_id = internal_transfer_stock_obj.create({'location_id':main_location_id.id,
                                                                        'location_dest_id':self.fleet_location_id.id,
                                                                        'picking_type_id':stock_location_type_id,
                                                                        'move_lines':move_list,
                                                                        'origin':self.sale_order_id.name,
                                                                        'sale_id':self.sale_order_id.id,
                                                                        'service_id':self.id,
                                                                        })
                view = self.env.ref('stock.view_immediate_transfer')
                new_picking_id.action_assign()
                wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, new_picking_id.id)]})
                return self.write({'is_transfer_main_to_truck':True})
            if not move_list:
                return self.write({'is_transfer_main_to_truck':True})
                
    @api.multi
    def stop_workorder(self):
        self.end_previous()
        state_obj = self.env['service.stage'].search(
            [('name', '=', 'Completed')], limit=1)
        return self.write({'state': 'completed', 'end_date': fields.Datetime.now(), 'stage_id': state_obj.id})
    
    
    customer_id=fields.Char(string="Customer number",compute='_get_customer_number')
    
    @api.depends('partner_id')
    def _get_customer_number(self):
        for service in self:
            if service.partner_id:
                service.customer_id=service.partner_id.id or False

    @api.onchange('customer_id')
    def onchnage_partner(self):
        customer_id = int(self.customer_id)
        if not self.customer_id:
            return {'domain': {'partner_shipping_id': [('customer','=',True),('custom_lead','=',False),('type','=','delivery')]}}
        else:
            domain=[('customer','=',True),('custom_lead','=',False),('type','=','delivery'),('parent_id','=',customer_id)]
            ship_res_id=self.env['res.partner'].search(domain,limit=1)
            if not ship_res_id:
                self.partner_shipping_id=self.partner_id.id
            else:
                self.partner_shipping_id=ship_res_id.id
            return {'domain': {'partner_shipping_id': domain}}
    
    


    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            
            
            addr = self.partner_id.address_get(['delivery', 'invoice'])
            values = {
                'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
                'partner_invoice_id': addr['invoice'],
#                 'partner_shipping_id': addr['delivery'],
                'equipment_id': False,
                'equipment_model_id': False,
                'equipment_make_id': False,
                'equipment_serial_number': False,
                'equipment_date_installed': False,
            }
            self.update(values)
            return

    @api.model
    def create(self, vals):
        vals.update({'is_plan_done': True})
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.service') or _('New')
        result = super(ServiceCustomerInformation, self).create(vals)
        return result

class StockLocation(models.Model):
    _inherit = "stock.location"
    
    service_id = fields.Many2one('service.customer.information',string = "Service Work order")
    
class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    service_id = fields.Many2one('service.customer.information',string = "Service Work order")
    is_truck_transfer = fields.Boolean(string="Is Truck",readonly=True)
    transfer_by = fields.Char(string="Transfer By",default=lambda self: self.env.user.name)

class customer_workcenter_productivity(models.Model):
    _name = "customer.workcenter.productivity"

    customer_workcenter_id = fields.Many2one(
        'service.customer.information', "Work Center")
    technician_id = fields.Many2one("res.users")
    date_start = fields.Datetime("Start Date")
    date_end = fields.Datetime("End Date")
    duration_line = fields.Float(
        "Time", compute='_compute_duration', store=True)
    description = fields.Text('Description')

    @api.depends('date_end', 'date_start')
    def _compute_duration(self):
        for blocktime in self:
            if blocktime.date_end:
                d1 = fields.Datetime.from_string(blocktime.date_start)
                d2 = fields.Datetime.from_string(blocktime.date_end)
                diff = d2 - d1
                blocktime.duration_line = round(diff.total_seconds() / 60.0, 2)
            else:
                blocktime.duration_line = 0.0


class ServiceEquipmentMake(models.Model):
    _name = "service.equipment.make"
    _description = "Service Equipment Make"

    name = fields.Char('Name')


class ServiceEquipmentModel(models.Model):
    _name = "service.equipment.model"
    _description = "Service Equipment Model"

    name = fields.Char('Name')

class ServiceInventoryWorkflow(models.Model):
    _name = "service.inventory.workflow"
    _description = "Service Inventory Workflow"

    service_customer_info_id = fields.Many2one(
        'service.customer.information', string="Service Customer Information")
    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), default=1.0)
    product_uom = fields.Many2one(
        'product.uom', string='Unit of Measure', related="product_id.uom_id")
    product_price = fields.Float(
        string="Price", related="product_id.list_price")
    inventory_source = fields.Selection([
        ('truck', 'Truck'),
        ('non_truck', 'Non-Truck'),
    ], string="Inventory Source")

class SaleOrderLine(models.Model):
    _inherit='sale.order.line'

    

    # use for float UOM while unit is hours
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not(self.product_uom.name == "Hour(s)"):
            self.product_uom_qty = round(self.product_uom_qty)
        rec = super(SaleOrderLine, self).product_uom_change()
        return rec


