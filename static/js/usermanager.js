var usermanager = angular.module("usermanager", []);

usermanager.controller("usersCtrl", function($scope, $http, $rootScope) {
    $http.get("/api/usermanager/users")
});
