odoo.define('maqpower_customized_crafito.custom_products', function(require) {
    "use strict";

    var base = require('web_editor.base');

    $('.oe_website_sale').each(function() {
        var oe_website_sale = this;

        $(oe_website_sale).on('change', 'input.custom_js_variant_change, select.custom_js_variant_change, ul[data-custom_attribute_value_ids]', function(ev) {
            var $ul = $(ev.target).closest('.js_custom_variants');
            var $parent = $ul.closest('#form_ask_for_quote');
            var $product_id = $parent.find('input.product_id').first();
            var variant_ids = $ul.data("custom_attribute_value_ids");
            var values = [];
            $parent.find('input.custom_js_variant_change:checked, select.custom_js_variant_change').each(function() {
                values.push(+$(this).val());
            });

            var product_id = false;
            for (var k in variant_ids) {
                if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                    product_id = variant_ids[k][0];
                    break;
                }
            }
            if (product_id) {
                $product_id.val(product_id);
            } else {
                $product_id.val(0);
            }
        });

        $('form#form_ask_for_quote').off('submit').on('submit', function(e) {
            if ($("input[name='cust_name']").val() == '') {
                $("div#cust_name").addClass("has-error");
                e.preventDefault();
            } else{
                $("div#cust_name").removeClass("has-error");
            }
            if ($("input[name='cust_email']").val() == '') {
                $("div#cust_email").addClass("has-error");
                e.preventDefault();
            } else{
                $("div#cust_email").removeClass("has-error");
            }
            if ($("input[name='cust_phone']").val() == '') {
                $("div#cust_phone").addClass("has-error");
                e.preventDefault();
            } else{
                $("div#cust_phone").removeClass("has-error");
            }
            if ($("input[name='prod_qty']").val() == '') {
                $("div#prod_qty").addClass("has-error");
                e.preventDefault();
            } else{
                $("div#prod_qty").removeClass("has-error");
            }
        });

    });
});