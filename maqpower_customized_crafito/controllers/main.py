
from odoo import http
from odoo.http import request
from odoo import models, fields
from odoo.addons.website_sale.controllers.main import WebsiteSale


class MaqpowerShop(WebsiteSale):

    def generate_so(self, partner_id, product_id, post):
        if post.get('quote_comment'):
            customer_comment = post.get('quote_comment')
        else:
            customer_comment = 'No Comment'

        sale_order = request.env['sale.order'].sudo().create({
            'partner_id': partner_id.id,
            'customer_comment': customer_comment,
            'date_order': fields.Datetime.now()
        })
        if sale_order:
            sale_order_line = request.env['sale.order.line'].sudo().create({
                'order_id': sale_order.id,
                'product_id': int(product_id),
                'product_uom_qty': post.get('prod_qty'),
                'price_unit': 0,
            })
        return True

    @http.route(['/shop/ask_for_quote'], type="http", auth="public", methods=['POST'], website=True)
    def ask_for_quote(self, product_id, **post):
        partner_obj = request.env["res.partner"]
        partner_id = partner_obj.sudo().search(
            [('email', '=', post.get('cust_email')), ('name', '=', post.get('cust_name'))])
        if partner_id:
            if post.get('cust_phone'):
                partner_id.write({'phone': post.get('cust_phone')})
            self.generate_so(partner_id, product_id, post)
        # else:
        #     partner_id = partner_obj.sudo().create({
        #         'name': post.get('cust_name'),
        #         'email': post.get('cust_email'),
        #         'phone': post.get('cust_phone'),
        #     })
        #     self.generate_so(partner_id, product_id, post)
        product = request.env['product.product'].search([('id', '=', int(product_id))])
        request.session.update({'quote_success': True})
        return request.redirect('/shop/product/%s?quote_success=True' % product.product_tmpl_id.id)
