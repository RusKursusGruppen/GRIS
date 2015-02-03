
gris.directive("isActiveNav", function($location) {
    return {
        restrict: "A",
        link: function(scope, element) {
            scope.location = $location;
            scope.$watch("location.path()", function(currentPath) {
                if ("/#" + currentPath === element[0].attributes["href"].value) {
                    element.parent().addClass("active");
                } else {
                    element.parent().removeClass("active");
                }
            });
        }
    };
});

gris.directive("gUser", function($location) {
    return {
        scope: { user: "=user" },
        template: "<a href='' class='user' tooltip='{{user.name}}'><i class='fa fa-user'></i> {{user.username}}</a>"
    };
});

gris.directive("gRustourType", function() {
    return {
        scope: { tour: "=tour" },
        template:
        "<span ng-switch='tour.type'>" +
            "<span ng-switch-when='m' tooltip='Munketur'><i class='fa fa-mars'></i></span>" +
            "<span ng-switch-when='p' tooltip='Pigetur'><i class='fa fa-venus'></i></span>" +
            "<span ng-switch-when='t' tooltip='Transetur'><i class='fa fa-transgender'></i></span>" +
            "<span ng-switch-default tooltip='Uvist type'><i class='fa fa-circle-thin'></i></span>" +
        "</span>"

    };
});
