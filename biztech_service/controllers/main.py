# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo import api, http, SUPERUSER_ID, _

class ServiceController(http.Controller):

    @http.route(['/service/get_default_data'], type="json", auth="public")
    def get_default_data(self, **post):

        if post and post.get('fields') and post.get('model'):

            fields = post.get('fields')
            model = post.get('model')

            fields_with_data = request.env[model].sudo().default_get(fields)
            return fields_with_data
        else:
            return False


class WebsiteForm(WebsiteForm):
    
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)   
    def website_form(self, model_name, **kwargs):
        mails_to_send = request.env['mail.mail']
        res = super(WebsiteForm, self).website_form(model_name, **kwargs)
        ir_model_data = request.env['ir.model.data']
        invitation_template = request.env["ir.model.data"].sudo().get_object('biztech_service', 'email_template_customer_create')[0]
        if kwargs:
            if kwargs.get('contact_name'):
                rendering_context = dict(request._context)
                rendering_context.update({'name':kwargs.get('contact_name'),
                                          'user_id':SUPERUSER_ID,
                                          'phone':kwargs.get('phone'),
                                          'email_from':kwargs.get('email_from'),
                                          'country':kwargs.get('partner_name'),
                                          'subject':kwargs.get('name')
                })
            invitation_template = invitation_template.with_context(rendering_context)
            mail_id = invitation_template.send_mail(SUPERUSER_ID)
            current_mail = request.env['mail.mail'].browse(mail_id)
            mails_to_send |= current_mail
            mails_to_send.send(mail_id)
        return res
    
class ResPartner(http.Controller):
    
    @http.route(['/biztech_service/delete_record'], type="json", auth="public")
    def hide_delete_button_access(self, **post):
        module_category_id= request.env['ir.module.category'].search([('name','=','Extra Rights')])
        if module_category_id:
            delete_group_ids = request.env['res.groups'].search([('name','=','Delete'), ('category_id', '=', module_category_id.id)])
            uid=request.env.user
            for group_id in delete_group_ids:
                request._cr.execute("select uid from res_groups_users_rel where gid=%s", (group_id.id,))
                r = request._cr.fetchall()
                for user_id in r:
                    if uid.id == user_id[0]:
                        return True
        return False
    
    @http.route(['/biztech_service/create_contact_kanban'], type="json", auth="public")
    def hide_create_button_access(self, **post):
        if post.get('model')=='res.partner':
            module_category_id= request.env['ir.module.category'].search([('name','=','Extra Rights')])
            if module_category_id:
                delete_group_ids = request.env['res.groups'].search([('name','=','Create'), ('category_id', '=', module_category_id.id)])
                uid=request.env.user
                for group_id in delete_group_ids:
                    request._cr.execute("select uid from res_groups_users_rel where gid=%s", (group_id.id,))
                    r = request._cr.fetchall()
                    for user_id in r:
                        if uid.id == user_id[0]:
                            return True
            return False
    
    