function displaynl () {
    jQuery('.fadercontrol').hide();
    jQuery('.older-newsletter').fadeIn('slow');
}

var OSHMAIL = {}

OSHMAIL.loadOshmailContent = function () {
    jQuery.fancybox.showActivity();
    jQuery.ajax({
        async: false,
        type: 'GET',
        url: this.href,
        success: function(data) {
            var stuff = jQuery(data).find("#collage");
            jQuery("#oshmail-overlay #collage")
                .replaceWith(function() {
                    console.log(stuff);
                    return stuff;
                });
            jQuery.fancybox.hideActivity();
            jQuery("div#fancybox-wrap").unbind("mousewheel");
        }
    });
};

jQuery(document).ready(function() {
    if (jQuery("a[rel=oshmail-fancybox]").length>0) {
        jQuery("a[rel=oshmail-fancybox]")
            .fancybox({
                'transitionIn'      : 'elastic',
                'transitionOut'     : 'elastic',
                'titlePosition'     : 'over',
                'overlayOpacity'    : 0.7,
                'overlayColor'      : '#FFF',
                'showNavArrows'     : false,
                'autoScale'         : false,
                'autoDimensions'    : false,
                'enableKeyboardNav' : false,
                'width'             : jQuery(window).width() - 100,
                'height'            : jQuery(window).height() - 100,
                'content'           : jQuery('#oshmail-overlay'),
                'onComplete'        : OSHMAIL.loadOshmailContent,
                'onCleanup'         : function() {
                    jQuery("#oshmail-overlay #collage")
                        .css({"opacity" : "0",});
                },
            });
    }
})

