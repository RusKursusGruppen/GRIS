
gris.controller("newsCtrl", function($scope, $http, $rootScope) {
    $rootScope.submenu = [{href:"/#/news/create", text:"Ny nyhed", click:""}];
    $http.get("/api/news")
        .success(function(data) {
            $scope.news = data.values;
        });

    $scope.editing = null;
    $scope.old_title = null;
    $scope.old_body = null;

    $scope.edit = function(article) {
        // Cancel ongoing edit
        if ($scope.editing != null) {
            $scope.cancel();
        }
        $scope.editing = article;
        $scope.old_title = article.title;
        $scope.old_body = article.body;

        console.log(article);
        console.log($scope.editing);
        console.log($scope.old_article);
    };

    $scope.cancel = function() {
        $scope.editing.title = $scope.old_title;
        $scope.editing.body = $scope.old_body;
        $scope.editing = null;
    };

    $scope.submit = function() {
        $http.post("/api/news/update", $scope.editing);
        $scope.old_title = null;
        $scope.old_body = null;
        $scope.editing = null;
    };

    $scope.delete = function() {
        $http.post("/api/news/delete", {news_id: $scope.editing.news_id});
        $scope.news = $scope.news.filter(function(item) {
            return item !== $scope.editing;
        });
        $scope.old_title = null;
        $scope.old_body = null;
        $scope.editing = null;

    };
});

gris.controller("newsCreateCtrl", function($scope, $http, $location) {
    $scope.title = "";
    $scope.body = "";

    $scope.editing = null;
    $scope.create_new = function(form) {
        if (!form.$invalid) {
            $http.post("/api/news/new", {title:$scope.title, body:$scope.body});
            $location.url("/#/news");
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
