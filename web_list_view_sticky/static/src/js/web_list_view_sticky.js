odoo.define('web_list_view_sticky.web_list_view_sticky_js', function(require) {
    "use strict";

    var core = require('web.core');
    var BasicRenderer = require('web.BasicRenderer');
    var _t = core._t;
    BasicRenderer.include({
        _renderView: function() {
            var self = this;
        self._super.apply(this, arguments);
            setTimeout(function() {
                var form_field_length = self.$el.parents('.o_form_field').length;
                var scrollArea = $(".o_content")[0];

                function do_freeze () {
                    self.$el.find('table.o_list_view').each(function () {
                        $(this).stickyTableHeaders({scrollableArea: scrollArea, fixedOffset: 0.1});
                    });
                }

                if (form_field_length == 0) {
                    do_freeze();
                    $(window).unbind('resize', do_freeze).bind('resize', do_freeze);
                }
            }, 2);
            return $.when();
        }
    });
});