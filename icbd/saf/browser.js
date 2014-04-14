$(document).ready(function() {
    var clicked = null;
    var highlighted = null;

    highlight = function(el) {
        highlighted = el;

        var idx = el.getAttribute('type_idx')
        var t = type_table[idx];
        if (idx in instance_table) {
            idx = instance_table[idx];
            t = "instance of " + type_table[idx];
        }
        var html = "<code>" + el.innerText + "</code>";
        if (idx === null) html += " could not be analyzed";
        else if (idx === "") html += " had no found types";
        else html += " has type <code>" + t + "</code>";

        if (idx in class_table) {
            html += "<pre>"
            html += "C class members:<ul>"
            var d = class_table[idx]['cls_attrs'];
            for (p in d) {
                html += "<li>" + p + " : " + type_table[d[p]] + "</li>"
            }
            html += "</ul>"
            html += "C instance members:<ul>"
            d = class_table[idx]['inst_attrs']
            for (p in d) {
                html += "<li>" + p + " : " + type_table[d[p]] + "</li>"
            }
            html += "</ul>"
            html += "</pre>"
        }
        $("#sidebar").html(html);
        //$("span.anno").addClass("semihighlight");
        for (var i = 0; i < el.classList.length; i++) {
            cls = el.classList[i];
            if (cls.indexOf("usedef") == 0) {
                $("." + cls).addClass("semihighlight");
            }
        }
        $(highlighted).addClass("activehighlight");
    }
    unhighlight = function() {
        if (!highlighted)
            return;
        $(highlighted).removeClass("activehighlight");
        $(".semihighlight").removeClass("semihighlight");
        highlighted = null;
    }
    $("span.anno").on('mouseover', function(e) {
        unhighlight();
        highlight(e.target);
    });
    $("span.anno").on('click', function(e) {
        if (clicked == e.target) {
            clicked = null;
        } else {
            clicked = e.target;
        }
    });
    $('span.anno').on('mouseout', function(e) {
        unhighlight();
        if (clicked)
            highlight(clicked);
    });
});
