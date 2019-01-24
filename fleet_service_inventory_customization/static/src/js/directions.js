odoo.define('fleet_service_inventory_customization.directions_js', function(require) {
    "use strict";
    $(document).ready(function() {
		var href = window.location.href
		var link_contains = 'view_type=form&model=service.customer.information'
		var core = require('web.core');
		var ajax = require('web.ajax');
		var qweb = core.qweb;
		var self = this;
		var id = $('.o_form_binary_form').find("input[name='id']").val();
		var model =$('.o_form_binary_form').find("input[name='model']").val();
		var field_result;
		var FormRenderer = require('web.FormRenderer')
		var innerHTML;
		return FormRenderer.include({
			init: function(node){
				var widget = this._super.apply(this, arguments);
	            var model = this.state.model;
	            var res_id = this.state.res_id;
	            var data = this.state.data;
			
		ajax.jsonRpc('/fleet_location/get_data', 'call',{
			rec_id:res_id,
			method:'_get_address',
			model:'service.customer.information',
			
		}).done(function(fields_with_data){
			if (fields_with_data != false) {
					fields_with_data['origin']
					fields_with_data['destination']
					var directionsDisplay, directionsService;
					var map;
					var directionsService = new google.maps.DirectionsService();
					var service = new google.maps.DistanceMatrixService();
					var request = {
							
					  origin      : fields_with_data['origin'], // a city, full address, landmark etc
					  destination : fields_with_data['destination'],
					  travelMode  : google.maps.DirectionsTravelMode.DRIVING,
					  unitSystem: google.maps.UnitSystem.METRIC,
					};
					directionsService.route(request, function(response, status) {
						if (status == google.maps.DistanceMatrixStatus.OK){
							ajax.jsonRpc('/fleet_location/set_data/time', 'call',{
							minut:response.routes[0].legs[0].duration.text,
							rec_id:res_id	
							})
							.done(function(fields_set_data){
								})
//							alert(response.routes[0].legs[0].duration.text);
							}
						if ( status == google.maps.DirectionsStatus.OK ) {
							ajax.jsonRpc('/fleet_location/set_data', 'call',{
								miles:response.routes[0].legs[0].distance.value/1609.344,
								model:'service.customer.information',
								rec_id:res_id
								}).done(function(fields_set_data){
									})
					  }
					});
				   };
		    	});
			}
		})
	            
	})
    })
