/* Credit to http://azmind.com/demo/bootstrap-multi-step-registration-form/ */

jQuery(document).ready(function() {
		  $.backstretch("static/img/robot_love.jpg");

    /*
        Fullscreen background
    */
//     $.backstretch("assets/img/backgrounds/1.jpg");
//     
//     $('#top-navbar-1').on('shown.bs.collapse', function(){
//     	$.backstretch("resize");
//     });
//     $('#top-navbar-1').on('hidden.bs.collapse', function(){
//     	$.backstretch("resize");
//     });
//     
    /*
        Form
    */
    $('.registration-form fieldset:first-child').fadeIn('slow');
    
    $('.registration-form input[type="text"], .registration-form input[type="password"], .registration-form textarea').on('focus', function() {
    	$(this).removeClass('input-error');
    });
    
    // next step
    $('.registration-form .btn-next').on('click', function() {
    	var parent_fieldset = $(this).parents('fieldset');
    	var next_step = true;
    	
    	parent_fieldset.find('input[type="text"], input[type="password"], textarea').each(function() {
    		if( $(this).val() == "" ) {
    			$(this).addClass('input-error');
    			next_step = false;
    		}
    		else {
    			$(this).removeClass('input-error');
    		}
    	});
    	
    	if( next_step ) {
    		parent_fieldset.fadeOut(400, function() {
	    		$(this).next().fadeIn();
	    	});
    	}
    	
    });
    
    // previous step
    $('.registration-form .btn-previous').on('click', function() {
    	$(this).parents('fieldset').fadeOut(400, function() {
    		$(this).prev().fadeIn();
    	});
    });
     $( "#sortable" ).sortable({ axis: "y", containment: "#social_rank_container", scroll: false }).disableSelection();


    // submit
    $('.registration-form').on('submit', function(e) {
    	
    	$(this).find('input[type="text"], input[type="password"], textarea').each(function() {
    		if( $(this).val() == "" ) {
    			e.preventDefault();
    			$(this).addClass('input-error');
    		}
    		else {
    			$(this).removeClass('input-error');
    		}
    	});
		    $('#social-rankings').val($( "#sortable" ).sortable("serialize"));
		
    });
        //
        // $('.login-form').on('click', function(e) {
		// 	//	$('#default').val('\x12\xb2\xd3?\xf4\xf6\x0f\xa1\xe9\r4\x02\xdbM\xc0r')
		// 	$('.login-form').submit()
		// })

    
//     
//    $("#distance-slider").slider({
// 	tooltip: 'always'
// });

    
});
