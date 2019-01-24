odoo.define('quotation_service_work_order.contatc_send_message_js', function(require) {
    "use strict";
    $(document).on('click','#send_msg', function(event) {
    	setTimeout(function(){$(".o_chatter_button_new_message").trigger('click');}, 800);
    });
    });

