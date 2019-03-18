odoo.define('biztech_service.kanban_false', function (require){
    var KanbanColumn = require('web.KanbanColumn');

    KanbanColumn.include({
        init: function(){
            var res = this._super.apply(this, arguments);
            if (this.modelName === 'service.customer.information') {
                this.draggable = false;
            }
            return res;
        }
    });
});