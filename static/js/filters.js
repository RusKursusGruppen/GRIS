gris.filter("rustourType", function() {
    return function(input) {
        switch (input) {
        case "m": return "Munketur";
        case "p": return "Pigetur";
        case "t": return "Transetur";
        default: return "Uvist type";
        }
    }
});

gris.filter("rustourTypeIcon", function() {
    return function(input) {
        switch (input) {
        case "Munketur":
        case "m": return '<i class="fa fa-mars"></i>';
        case "pigetur":
        case "p": return '<i class="fa fa-venus"></i>';
        case "Transetur":
        case "t": return '<i class="fa fa-transgender"></i>';
        default: return '<i class="fa fa-circle-thin"></i>';
        }
    }
});
