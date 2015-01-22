
var news = angular.module("news", []);

news.controller("newsCtrl", function($scope, $http) {
    $http.get("/api/news").success(function(data) {
        $scope.news = data.values;
    });

    $scope.test = false;

    $scope.create_new = function(form) {
        if (!form.$invalid) {
            $http.post("/api/news/new", {title:$scope.title, body:$scope.body});
            $scope.cancel(form);
        }
    };

    $scope.cancel = function(form) {
        $scope.title = "";
        $scope.body = "";
        if (form) {
            form.$setPristine();
            form.$setUntouched();
        }
        $scope.creating_mode = false;
    };
    $scope.cancel();
});
