odoo.define('enterprise_sorted_apps.custom_app_switcher_js', function (require) {
"use strict";

var AppSwitcher = require('web_enterprise.AppSwitcher');

    return AppSwitcher.include({
        
        get_initial_state: function() {
            var res = this._super.apply(this)

            var sorted_apps = _.sortBy(res.apps, 'label');
            var new_apps = new Array();
            _.each(sorted_apps, function(r){
                new_apps.push(r);
            });
            res.apps = new_apps

            return res
        }
    });
});
