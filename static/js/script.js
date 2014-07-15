																																																																							// MASONRY
// =================================================================================================

$(window).load(function() {
	if ($(window).width() > 960) {
		$('.landscape .thumbnails').masonry({ 
			columnWidth: 176, 
			itemSelector: '.thumbnail' 
		});
		$('.landscape.full .thumbnails, .portrait.full .thumbnails').masonry({ 
			columnWidth: 186, 
			itemSelector: '.thumbnail' 
		});
		$('#archive-posts').masonry({ 
			columnWidth: 248, 
			itemSelector: '.archive-post' 
		});
	}
	else if ($(window).width() < 769) {
		$('.landscape .thumbnails').masonry({ 
			columnWidth: 176,
			itemSelector: '.thumbnail' 
		});
		$('.landscape.full .thumbnails, .portrait.full .thumbnails').masonry({ 
			columnWidth: 182, 
			itemSelector: '.thumbnail' 
		});
		$('#archive-posts').masonry({ 
			columnWidth: 242, 
			itemSelector: '.archive-post' 
		});
	}
	else if ($(window).width() < 601) {
		$('.landscape .thumbnails').masonry({ 
			columnWidth: 176,
			itemSelector: '.thumbnail' 
		});
		$('.landscape.full .thumbnails, .portrait.full .thumbnails').masonry({ 
			columnWidth: 182, 
			itemSelector: '.thumbnail' 
		});
	}
});

$(window).resize(function() {
  if(detector.outerWidth(true)!=curWidth){
  	curWidth = detector.outerWidth(true);
	  $wall.masonry( 'option', { columnWidth: curWidth });
  }
});

// COLORBOX
// =================================================================================================

$(document).ready(function() {
	if ($(window).width() > 960) {
		$(".hero a, .thumbnails a, .images a").colorbox({
			transition:"elastic", 
			maxWidth:"98%", 
			maxHeight:"98%"
		});
		$("a.lightbox").colorbox({
			transition:"elastic",
			maxWidth:"98%",
			maxHeight:"98%"
		});
	}
});