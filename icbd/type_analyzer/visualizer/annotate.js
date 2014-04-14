$(document).ready(function() {
    var highlighted = null;
    $("span.anno").on('mouseover', function(e) {
        type_str = type_table[e.target.id];
        col_str = e.target.id.split('_')[0];
        preview_id = '#col_' + col_str;
        var new_highlighted = $(preview_id);
        if (new_highlighted != highlighted) {
            if (highlighted) highlighted.innerHTML = "";
            highlighted = new_highlighted;
            if (highlighted.hasClass('slide')) {
                type_str = type_str + ' ';
            } else {
                type_str = ' ' + type_str;
            }
            highlighted[0].innerHTML = type_str;
            if (highlighted[0].style.width === "") {
                highlighted[0].style.width = 0;
            }
            highlighted.stop(true, true);
            if (highlighted.hasClass('slide')) {
                target_width = Math.max(highlighted[0].scrollWidth, highlighted[0].offsetWidth);
                highlighted.animate({width: target_width, opacity: 1});
            } else {
                highlighted.fadeIn(200);
            }
        }
    });
    $('span.anno').on('mouseout', function(e) {
        if (highlighted) {
            if (highlighted.hasClass('slide')) {
                highlighted.animate({width: '0', opacity: '0'});
            } else {
                highlighted.fadeOut(200);
            }
            highlighted = null;
        }
    });
});
