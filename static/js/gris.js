"use strict";


var gris = angular.module("gris", ["ngRoute", "ngSanitize"]);

gris.config(function($routeProvider) {
    $routeProvider.
        when("/", {
            redirectTo: "/news"
        })
        .when("/login", {
            templateUrl: "/static/html/login.html",
            controller: "loginCtrl"
        })
        .when("/news", {
            templateUrl: "/static/html/news.html",
            controller: "newsCtrl"
        })
        .when("/news/create", {
            templateUrl: "/static/html/news-create.html",
            controller: "newsCreateCtrl"
        })
        .when("/users", {
            templateUrl: "/static/html/users.html",
            controller: "usersCtrl"
        })
        .when("/rustours", {
            templateUrl: "/static/html/rustours.html",
            controller: "rustoursCtrl",
            reloadOnSearch: false
        })
        .otherwise({
            templateUrl: "/static/html/urlnotfound.html"
        });
});

gris.controller("grisCtrl", function($scope, $rootScope, $http, $location) {
    $rootScope.local_menu = [];
    $rootScope.logged_in = null;
    $scope.check_logged_in = function() {
        if (!$rootScope.logged_in) {
            $http.get("/api/usermanager/logged_in")
                .success(function(data) {
                    if (data.logged_in) {
                        $rootScope.logged_in = true;
                        $rootScope.me = data.user;
                    } else {
                        $rootScope.logged_in = data.logged_in;
                        $location.url("/login");
                    }})
                .error(function(data) {
                    console.log("Could not call logged_in: ", data);
                });
        }
    };
    $scope.$on("$routeChangeStart", function(next, current) {
        $scope.check_logged_in();
    });
    $scope.check_logged_in();

    $scope.logout = function() {
        $http.post("/api/usermanager/logout");
        $rootScope.logged_in = false
        $rootScope.me = null;
    };
});
