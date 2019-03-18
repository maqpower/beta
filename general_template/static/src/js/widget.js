odoo.define('general_template.color', function(require) {
    "use strict";

    var core = require('web.core');
    var form_widgets = require('web.basic_fields');
    var field_registry = require('web.field_registry');
    var FormController = require('web.FormController');

    var _t = core._t;


    var _super_getDir = jscolor.getDir.prototype;
    jscolor.getDir = function() {
        var dir = _super_getDir.constructor();
        if (dir.indexOf('web_widget_color') === -1) {
            jscolor.dir = 'general_template/static/lib/jscolor/';
        }
        return jscolor.dir;

    };

    core.search_widgets_registry.add('color', 'instance.web.search.CharField');


    var FieldColor = form_widgets.FieldChar.extend({
        template: 'FieldColor',
        widget_class: 'oe_form_field_color',
        _onChange: function() {
            if (this.mode != 'readonly' && this.$('input').length && this.is_syntax_valid()) {   
                this._setValue(
                        this._parseValue(this.$('input').val()));
            }
        },
        is_syntax_valid: function() {
            var $input = this.$('input');
            if (this.mode == 'edit' && $input.size() > 0) {
                var val = $input.val();
                var isOk = /^#[0-9A-F]{6}$/i.test(val);
                if (!isOk) {
                    return false;
                }
                try {
                    this._parseValue(this.$('input').val());
                    this._isValid = true;
                    return true;
                } catch (e) {
                    return false;
                }
            }
            return true;
        },

        // render_value: function() {
        _render: function() {
            var show_value = this._formatValue(this.value);

            if (this.mode == 'edit') {
                var $input = this.$el.find('input');
                $input.val(show_value);
                $input.css("background-color", show_value)
                jscolor.init(this.$el[0]);
            } else if(this.mode == 'readonly') {
                this.$(".oe_form_char_content").text(show_value);
                this.$('div').css("background-color", show_value)
            }
        }
    });

    field_registry.add('color', FieldColor);

    /*
     * Init jscolor for each editable mode on view form
     */
    FormController.include({
        _onEdit: function() {
            this._super();
            jscolor.init(this.$el[0]);
        }
    });
});