from odoo import models, api, fields, _

#Add domain for Mfg fiscal position in customer form
class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    show_in_customer=fields.Boolean(string="Show In Customer")

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    customer_number=fields.Char(string="Customer Number")
    create_from_script = fields.Boolean("Facility Operations List")
    privious_destribute = fields.Boolean("Previous Distributor Customer")
    main_contatc_create_for_history=fields.Boolean('Main Contact Related History')
    customer_id=fields.Char(string="Customer ID")
    mfg_tax_eligible=fields.Boolean(string="Mfg Tax Eligible?",track_visibility='onchange')

    @api.onchange('mfg_tax_eligible')
    def onchange_mfg_tax_eligible(self):
        if self.mfg_tax_eligible:
            return {'domain': {'property_account_position_id': [('show_in_customer','=',True)]}}
        else:
            return {'domain': {'property_account_position_id': [('show_in_customer','=',False)]}}

    @api.model
    def create(self, vals):
        if self._context.get('default_supplier'):
            vals.update({'custom_lead':0})
        if vals.get('parent_id'):
            ship_bill_id = self.search([('parent_id', '=', vals.get('parent_id')),('type', '=', vals.get('type')),('customer_number', '!=', '')],order='id desc', limit=1)
            if ship_bill_id:
                if vals.get('type') in ['delivery','invoice']:
                    if vals.get('type') == 'delivery':
                        custo_num = ship_bill_id.customer_number.split('S')[1]
                        count = int(custo_num)+1
                        customer_number = str(vals.get('parent_id')) + '-S' + str(count)
                        vals.update({'customer_number' : customer_number})
                    else:
                        custo_num = ship_bill_id.customer_number.split('B')[1]
                        count = int(custo_num)+1
                        customer_number = str(vals.get('parent_id')) + '-B' + str(count)
                        vals.update({'customer_number' : customer_number})
            else:
                if vals.get('type')== 'delivery':
                    customer_number = str(vals.get('parent_id')) + '-S' + str(1)
                    vals.update({'customer_number' : customer_number})
                else:
                    customer_number = str(vals.get('parent_id')) + '-B' + str(1)
                    vals.update({'customer_number' : customer_number})
            result = super(ResPartner, self).create(vals)
            result.customer_id = result.id
            return result
        else:
            result = super(ResPartner, self).create(vals)
            result.customer_id = result.id
            return result
     
    @api.onchange('parent_id')
    def onchange_parent_type_id(self):
        if not self.parent_id:
            self.type ='contact'
         
    
    @api.multi
    def write(self, vals):
        rec = super(ResPartner, self).write(vals)
        if vals.get('parent_id') or vals.get('type') in ['invoice','delivery']:
            ship_bill_id = self.search([('parent_id', '=', self.parent_id.id),('type', '=', self.type),('id','!=', self.id),('customer_number', '!=', '')],order='id desc', limit=1)
            if ship_bill_id:
                if self.type in ['delivery','invoice']:
                    if self.type == 'delivery':
                        custo_num = ship_bill_id.customer_number.split('S')[1]
                        count = int(custo_num)+1
                        customer_number = str(self.parent_id.id) + '-S' + str(count)
                        self.customer_number = customer_number
                    if self.type == 'invoice':
                        custo_num = ship_bill_id.customer_number.split('B')[1]
                        count = int(custo_num)+1
                        customer_number = str(self.parent_id.id) + '-B' + str(count)
                        self.customer_number = customer_number
                else:
                    self.customer_number=''
            else:
                if self.type == 'delivery':
                    customer_number = str(self.parent_id.id) + '-S' + str(1)
                    self.customer_number = customer_number
                if self.type == 'invoice':
                    customer_number = str(self.parent_id.id) + '-B' + str(1)
                    self.customer_number = customer_number
        return rec
