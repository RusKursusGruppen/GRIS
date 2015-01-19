
var news = angular.module("news", []);

news.controller("newsCtrl", function($scope) {
    $scope.news = [{title:"hi", body:"Hello, World!", created:"12:49", creator:"23141"}, {title:"abc", body:"def", created:"12:49", creator:"23141"}];
    $scope.name = "Hello"
});
