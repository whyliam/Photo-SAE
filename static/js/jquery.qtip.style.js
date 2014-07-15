$(document).ready(function() {	
	if ($(window).width() > 960) {
		$('nav a[title]').qtip({
			show: 'mouseover',
			hide: 'mouseout',
			position: {
				corner: {
					target: 'topMiddle',
					tooltip: 'bottomMiddle',
				},					
				adjust: {
					x: 0, y: -5
				}
			},
			style: { 
				padding: 10,
				background: '#565350',
				color: '#f0ece7',
				textAlign: 'center',
				'font-size': 12,
				border: {
					width: 0,
					radius: 5,
					color: '#565350'
				},
				tip: 'bottomMiddle',
				name: 'dark'
			}			
		})
	}
});