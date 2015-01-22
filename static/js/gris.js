"use strict";

var grisApp = angular.module("grisApp", [
    "ngRoute",
    "login",
    "news"
]);

grisApp.config(function($routeProvider) {
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
        .otherwise({
            templateUrl: "/static/html/urlnotfound.html"
        });
});
