"use strict";

var grisApp = angular.module("grisApp", [
    "ngRoute",
    "news"
]);

grisApp.config(function($routeProvider) {
    $routeProvider.
        when("/", {
            redirectTo: "/news"
        }).
        when("/news", {
            templateUrl: "/static/html/news.html",
            controller: "newsCtrl"
        }).
        otherwise({
            templateUrl: "/static/html/urlnotfound.html"
        });
});
