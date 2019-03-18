odoo.define('biztech_service.access_js', function(require) {
    "use strict";
    
    var Sidebar = require('web.Sidebar');
    var ajax = require('web.ajax')
    var KanbanController = require('web.KanbanController');
    var KanbanRecord = require('web.KanbanRecord');

    $(window).load(function(){
        KanbanController.include({
            init: function (parent, options) {
                this._super.apply(this, arguments);
                var $ele = this
                if ($ele.modelName=='res.partner'){
                    ajax.jsonRpc('/biztech_service/create_contact_kanban', 'call', {
                        method: 'hide_create_button_access',
                        model:'res.partner',
                    }).then(function (result){
                        if (result == false){
                            self.$('button:contains("Create")').addClass('o_hidden');
                        }
                    })
                }
            },
        });
    });
    Sidebar.include({
        init : function(parent, options) {
            this._super.apply(this, arguments);
        },
        _redraw: function () {
            
            ajax.jsonRpc('/biztech_service/delete_record', 'call', {
                method: 'hide_delete_button_access',
            }).then(function (result){
                if (result == false){
                    self.$('a:contains(Delete)').addClass('o_hidden');
                }
            })
            
            this._super(this, arguments);
            if (this.env.model === "res.partner"){
                var def_create_statement = this._rpc({
                    
                    model: 'res.partner',
                    method: 'hide_create_button',
                    args: [{self: this.env.model}],
                    
                }).then(function (result){
                    if (result == false){
                        self.$('.o_form_button_create').addClass('o_hidden');
                        self.$('.o_list_button_add').addClass('o_hidden');
                        self.$('a:contains(Duplicate)').addClass('o_hidden');
                    }
                })
                    var def_edit_statement = this._rpc({
                    model: 'res.partner',
                    method: 'hide_edit_button',
                    args: [{self: this.env.model}],
                }).then(function (result){
                    if (result == false){
                        self.$('.o_form_button_edit').addClass('o_hidden');
                    }
                })
                    var def_delete_statement = this._rpc({
                    model: 'res.partner',
                    method: 'hide_delete_button',
                    args: [{self: this.env.model}],
                    
                }).then(function (result){
                    if (result == false){
                        self.$('a:contains(Delete)').addClass('o_hidden');
                    }
                })
        }
            
    }
    })
    
});
