var services = angular.module("services", []);

services.factory("Me", function($http) {
    me = {
        logged_in: null;
        check_logged_in : function() {
            if (this.logged_in == null) {
                $http.get("/api/usermanager/logged_in")
                    .success(function(data) {
                        this.logged_in = data.logged_in;
                    });
            }
        };
    };
});
