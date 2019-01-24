odoo.define('biztech_service.custom_tab_js', function(require) {
    "use strict";

    $(document).click(function(event) {
        var href = window.location.href
        var link_contains = 'view_type=form&model=service.customer.information'

        if (href.indexOf(link_contains) != -1) {
        //start time tracking tab color changes
        if (document.getElementById("stop_workorder")){
                var $time_tracking_note = $('div.change_notebook_tab_color')
                var $li_track_page = $time_tracking_note.find('li.end_date_service')
                if ($li_track_page && $li_track_page.find('a').hasClass('biz-tab-color')) {
                $li_track_page.find('a').removeClass('biz-tab-color')
                    $li_track_page.find('a').addClass('biz-success-tab-color')
                }
        }
        //end time tracking tab color changes
            var $element = $(event.target);
            var $parent_li = $element.parent()
            var $parent_div = $parent_li.closest('div')

            // to remove 0.00 val from float fields when clicked [not for 'ele_cv2' field]
            if ($element && $element.val() == '0.00') {
                $element.val('')
            }
            if ($element && $parent_div.hasClass('change_notebook_tab_color') && $parent_li.hasClass('active')) {
                var $ul = $parent_div.find('ul')
                if ($ul.hasClass('nav-tabs')) {
                    $ul.children().each(function() {
                        if ($(this).hasClass('active')) {
                            $(this).find('a').addClass('biz-tab-active-color')
                        } else if ($(this).find('a').hasClass('biz-tab-active-color')) {
                            $(this).find('a').removeClass('biz-tab-active-color')
                        }
                    });
                }
            }

            // for change tab color to green
            if ($element) {
                var $parent_div = $element.closest('div.tab-pane')
                var $active_tab = $('a.biz-tab-active-color')
                var len = 0
                var counter = 0
                var count_for_datepicker = 0
                var warning_counter = 0
                if ($parent_div.hasClass('tab-pane')) {
                    var $input_list = $parent_div.find('input.biz_warning')
                    var $select_list = $parent_div.find('select.biz_warning')
                    var $textarea = $parent_div.find('textarea.biz_warning')
                    if ($input_list) {
                        len = len + $input_list.length
                        $input_list.each(function() {
                            if ($(this).hasClass('color_green')) {
                                counter += 1
                            } else if ($(this).hasClass('biz_warning') && this.name != 'next_schedule_visit' && this.name != 'date_service_performed') {
                                warning_counter += 1
                            } else if ($(this).hasClass('biz_warning') && this.name == 'next_schedule_visit' && this.name != 'date_service_performed' && !$(this).parent('div').hasClass('o_invisible_modifier')) {
                                warning_counter += 1
                            }
                        });

                        // for date changes
                        var $o_datepicker_input_list = $parent_div.find('input.o_datepicker_input')
                        if ($o_datepicker_input_list) {
                            $o_datepicker_input_list.each(function() {
                                if ($active_tab && $active_tab[0].innerHTML == '* Service Wrap Up') {
                                    if ($(this).hasClass('biz-success-tab-color') && this.name == 'next_schedule_visit_success' && !$(this).parent('div').hasClass('o_invisible_modifier')) {
                                        count_for_datepicker += 1
                                    }
                                    if ($(this).hasClass('biz_warning') && this.name == 'next_schedule_visit' && $(this).parent('div').hasClass('o_invisible_modifier')) {
                                        count_for_datepicker += 1
                                    }
                                }
                                if ($active_tab && $active_tab[0].innerHTML == 'Scheduling Information') {
                                    if ( this.name == 'date_service_performed_success' && !$(this).parent('div').hasClass('o_invisible_modifier'))
                                    {
                                        if ($(this).hasClass('biz-success-tab-color'))
                                        {
                                            counter += 1
                                        }
                                        else if ($(this).hasClass('biz_warning'))
                                        {
                                            warning_counter += 1
                                        }
                                    }
                                    if ( this.name == 'date_service_performed' && !$(this).parent('div').hasClass('o_invisible_modifier'))
                                    {
                                        if ($(this).hasClass('biz-success-tab-color'))
                                        {
                                            counter += 1
                                        }
                                        else if ($(this).hasClass('biz_warning'))
                                        {
                                            warning_counter += 1
                                        }
                                    }
                                }
                            });
                            if ($active_tab && $active_tab[0].innerHTML == '* Service Wrap Up') {
                                if (count_for_datepicker == 2) {
                                    counter += 1
                                }
                            }
                        }
                    }
                    if ($select_list) {
                        len = len + $select_list.length
                        $select_list.each(function() {
                            if ($(this).hasClass('color_green')) {
                                counter += 1
                            } else if ($(this).hasClass('biz_warning')) {
                                warning_counter += 1
                            }
                        });
                    }
                    if ($textarea) {
                        len = len + $textarea.length
                        $textarea.each(function() {
                            if ($(this).hasClass('color_green')) {
                                counter += 1
                            } else if ($(this).hasClass('biz_warning')) {
                                warning_counter += 1
                            }
                        });
                    }
                }

                if (len > 0 && counter > 0 && len == counter && warning_counter == 0) {
                    var $main_notebook_div = $('div.change_notebook_tab_color')
                    var $li_tab = $main_notebook_div.find('li.active')
                    if ($li_tab && $li_tab.find('a').hasClass('biz-tab-color')) {
                        $li_tab.find('a').removeClass('biz-tab-color')
                        $li_tab.find('a').addClass('biz-success-tab-color')
                    }
                } else if (warning_counter > 0) {
                    var $main_notebook_div = $('div.change_notebook_tab_color')
                    var $li_tab = $main_notebook_div.find('li.active')
                    if ($li_tab && $li_tab.find('a').hasClass('biz-success-tab-color')) {
                        $li_tab.find('a').removeClass('biz-success-tab-color')
                        $li_tab.find('a').addClass('biz-tab-color')
                    }
                };
            }

            // for change date fields
            var $o_datepicker_input_list = $('input.o_datepicker_input')
            if ($o_datepicker_input_list) {
                $o_datepicker_input_list.each(function() {
                    if ($(this).hasClass('biz_warning') && this.name == 'next_schedule_visit_success') {
                        $(this).addClass('biz-success-tab-color')
                        $(this).removeClass('biz_warning')
                    }
                    if ($(this).hasClass('biz_warning') && this.name == 'date_service_scheduled') {
                        $(this).addClass('biz-success-tab-color')
                        $(this).removeClass('biz_warning')
                    }
                    if ($(this).hasClass('biz_warning') && this.name == 'date_service_performed_success') {
                        $(this).addClass('biz-success-tab-color')
                        $(this).removeClass('biz_warning')
                    }
                });
            }

            // for change many2one fields
            var $many2one_input_list = $('input.ui-autocomplete-input')
            if ($many2one_input_list) {
                $many2one_input_list.each(function() {
                    if ($(this).hasClass('biz_warning') && $(this)[0].value) {
                        $(this).addClass('color_green')
                    }
                });
            }
        }
    });

});