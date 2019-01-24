odoo.define('biztech_service.custom_js', function(require) {
    "use strict";
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var FormRenderer = require('web.FormRenderer')
    var ajax = require('web.ajax')

    var _t = core._t;
    var qweb = core.qweb;

    return FormRenderer.include({

        _renderTagNotebook: function(node) {
            var widget = this._super.apply(this, arguments);
            var model = this.state.model
            var res_id = this.state.res_id
            var data = this.state.data;
            
            if (widget.hasClass('change_notebook_tab_color') == true) {
                // added for active tab class - by Poonam
                widget.find('li.active').each(function() {
                    $(this).find("a").addClass('biz-tab-active-color')
                })

                widget.find('li.apply_color_action').each(function() {
                    $(this).find("a").addClass('biz-success-tab-color')
                });

                var $total_list_of_fields = widget.find('.o_field_widget')
                var $all_empty_fields = widget.find('.o_field_empty')
                var $float_field_list = widget.find('.o_field_float, .o_field_integer');
                var $all_empty_text_fields = widget.find('.o_field_char, .o_field_text, .o_input');
                var $all_empty_many2one_fields = widget.find('.ui-autocomplete-input');
                var $all_empty_datepicker_fields = widget.find('.o_datepicker_input');


                // all empty fields having the class o_field_empty, so...
                $all_empty_fields.each(function() {
                    var $div_id = $(this).closest("div[ id ^= 'notebook_page_']").first()

                    var $abc = $(this).closest(".o_notebook").find("a[href=#" + $div_id.attr('id') + "]")
                    if ($abc.parent().hasClass('apply_color_action') == true) {
                        if (!$(this).hasClass('ui-autocomplete-input')  && !$(this).hasClass('equipment_make') && !$(this).hasClass('equipment_model') && !$(this).hasClass('equipment_date_installed') && !$(this).hasClass('equipment_serial_number')) {
                            $abc.removeClass('biz-success-tab-color').addClass('biz-tab-color')
                            $(this).addClass('biz_warning')
                        }
                    }
                });

                // char field with empty data, so...
                $all_empty_text_fields.each(function() {
                    var $div_id = $(this).closest("div[ id ^= 'notebook_page_']").first()

                    if (data[$(this).attr('name')] == '') {

                        var $abc = $(this).closest(".o_notebook").find("a[href=#" + $div_id.attr('id') + "]")
                        if ($abc.parent().hasClass('apply_color_action') == true) {
                            if (!$(this).hasClass('ele_cv2') && this.name != 'ele_cv2' && !$(this).hasClass('count_duration') && this.name != 'count_duration' && !$(this).hasClass('total_duration') && this.name != 'total_duration' && this.name != 'end_date' && this.name != 'equipment_date_installed' && this.name != 'equipment_serial_number' && !$(this).hasClass('equipment_serial_number')) {
                                $abc.removeClass('biz-success-tab-color').addClass('biz-tab-color')
                                $(this).addClass('biz_warning')
                            }
                        }
                    }
                });

                // float number is always use 0.00 as default value, so...
                $float_field_list.each(function() {
                    var $div_id = $(this).closest("div[ id ^= 'notebook_page_']").first()

                    if (data[$(this).attr('name')] == 0.00) {
                        var $abc = $(this).closest(".o_notebook").find("a[href=#" + $div_id.attr('id') + "]")
                        if ($abc.parent().hasClass('apply_color_action') == true) {
                            if (!$(this).hasClass('ele_cv2') && this.name != 'ele_cv2' && !$(this).hasClass('total_duration') && !$(this).hasClass('count_duration')) {
                                $abc.removeClass('biz-success-tab-color').addClass('biz-tab-color')
                                $(this).addClass('biz_warning')
                                $(this).addClass('biz_validate')
                            }
                        }
                    }
                });

                // all empty many2one fields having the class ui-autocomplete-input, so...
                $all_empty_many2one_fields.each(function() {
                    var $div_id = $(this).closest("div[ id ^= 'notebook_page_']").first()
                    var $abc = $(this).closest(".o_notebook").find("a[href=#" + $div_id.attr('id') + "]")
                    if ($abc.parent().hasClass('apply_color_action') == true) {
                        if (!$(this).parent('div').parent('div').hasClass('equipment_make') && !$(this).parent('div').parent('div').hasClass('equipment_model') && !$(this).parent('div').parent('div').hasClass('stage_id') && !$(this)[0].value) {
                            $abc.removeClass('biz-success-tab-color').addClass('biz-tab-color')
                            $(this).addClass('biz_warning')
                        }
                    }
                });

                // all empty datepicker fields having the class o_datepicker_input, so...
                $all_empty_datepicker_fields.each(function() {
                    var $div_id = $(this).closest("div[ id ^= 'notebook_page_']").first()
                    var $abc = $(this).closest(".o_notebook").find("a[href=#" + $div_id.attr('id') + "]")
                    if ($abc.parent().hasClass('apply_color_action') == true) {
                        if (!$(this)[0].value && this.name != 'equipment_date_installed') {
                            $abc.removeClass('biz-success-tab-color').addClass('biz-tab-color')
                            $(this).addClass('biz_warning')
                        }
                    }
                });


                var field_list = [];
                $total_list_of_fields.each(function() {
                    field_list.push($(this).attr('name'));
                });

                var ajax_list;
                ajax.jsonRpc('/service/get_default_data', 'call', {
                    curr_id: res_id,
                    fields: field_list,
                    model: model,
                }).done(function(ajax_list) {

                    if (ajax_list != false) {

                        $total_list_of_fields.each(function() {
                            var $div_id = $(this).closest("div[ id ^= 'notebook_page_']").first()
                            var curr_name = $(this).attr('name');

                            if (_.has(ajax_list, curr_name)) {
                                if (_.isEqual(String(data[curr_name]), String(ajax_list[curr_name]))) {

                                    var $abc = $(this).closest(".o_notebook").find("a[href=#" + $div_id.attr('id') + "]")
                                    if ($abc.parent().hasClass('apply_color_action') == true) {
                                        if (this.name != 'no_of_service_units' && !$(this).hasClass('no_of_service_units')) {
                                            $abc.removeClass('biz-success-tab-color').addClass('biz-tab-color')
                                            $(this).addClass('biz_warning')
                                        }
                                    }
                                }
                            }
                            // ======================================================
                            // change color of the YES No field 
                            // ======================================================
                            if ($(this).hasClass('center_me')) {

                                $(this).css('font-weight', 'bold');
                                $(this).parent().attr('align', 'center');
                                if ($(this).html() == 'YES') {
                                    $(this).css("background-color", "green");
                                }
                            }


                        });
                    }
                });


                // changes of dropdown for selection on yes-no fields only
                widget.find('select.center_me').each(function() {
                    function color_changer(self) {
                        if ($(self).val()) {
                            var actual_val = $(self).val().slice(1, -1)
                            if (actual_val == 'yes') {
                                $(self).removeClass('color_red')
                                $(self).addClass('color_green')
                            } else if (actual_val == 'no' || actual_val == 'als') {
                                $(self).removeClass('color_green')
                                $(self).addClass('color_red')
                            }
                        } else {
                            $(self).removeClass('color_green')
                            $(self).addClass('color_red')
                        }
                    }

                    // change color on first load
                    color_changer(this)

                    $(this).on('change', function() {
                        color_changer(this)
                    });
                });
                widget.find('input.biz_validate').on('change', function() {
                	var x = false
                    if ($(this).val() != 0.00) {
                    	if (Number($(this).val())) {
                    	}
                    	else {
                    		var x= Dialog.alert(self, _t("Only numeric values are allowed"))
                    		$(this).focus();
                    		}
                    	}
                });
                
                widget.find('input.biz_warning').on('change', function() {
                    if ($(this).val() != 0.00) {
                        $(this).removeClass('color_red')
                        $(this).addClass('color_green')
                    }
                    if ($(this).val() == 0.00) {
                        $(this).addClass('color_red')
                        $(this).removeClass('color_green')
                    }
                });
             // only for CV2 field in Electronic tab
                widget.find('input.ele_cv2').each(function() {
                    if ($(this).hasClass('ele_cv2') && this.name == 'ele_cv2') {
                         {
                            $(this).addClass('ele_cv2_color_green')
                        }
                    }
                });

                // only for location field
                widget.find('select.biz_warning').on('change', function() {
                    function location_color_changer(self) {
                        if (self.name == 'service_location') {
                            if ($(self).val()) {
                                var actual_val = $(self).val().slice(1, -1)
                                if (actual_val == 'indoor' || actual_val == "outdoor") {
                                    $(self).removeClass('color_red')
                                    $(self).addClass('color_green')

                                } else {
                                    $(self).removeClass('color_green')
                                    $(self).addClass('color_red')
                                }
                            } else {
                                $(self).removeClass('color_green')
                                $(self).addClass('color_red')
                            }
                        }
                    }

                    // change color on first load
                    location_color_changer(this)
                    $(this).on('change', function() {
                        location_color_changer(this)
                    });
                });

                // only for Recommendations field 
                widget.find('textarea.biz_warning').on('change', function() {
                    if ($(this)[0].name == 'recommendations') {
                        if ($(this).val()) {
                            $(this).removeClass('color_red')
                            $(this).addClass('color_green')
                        } else {
                            $(this).addClass('color_red')
                            $(this).removeClass('color_green')
                        }
                    }
                    if ($(this)[0].name == 'equipment_compressor') {
                        if ($(this).val()) {
                            $(this).removeClass('color_red')
                            $(this).addClass('color_green')
                        } else {
                            $(this).addClass('color_red')
                            $(this).removeClass('color_green')
                        }
                    }
                    if ($(this)[0].name == 'equipment_location') {
                        if ($(this).val()) {
                            $(this).removeClass('color_red')
                            $(this).addClass('color_green')
                        } else {
                            $(this).addClass('color_red')
                            $(this).removeClass('color_green')
                        }
                    }
                    if ($(this)[0].name == 'work_details') {
                        if ($(this).val()) {
                            $(this).removeClass('color_red')
                            $(this).addClass('color_green')
                        } else {
                            $(this).addClass('color_red')
                            $(this).removeClass('color_green')
                        }
                    }
                });
            }

            return widget
        },
    });
});