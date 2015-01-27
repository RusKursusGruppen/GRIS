gris.controller("loginCtrl", function($scope, $http, $location, $rootScope) {
    $scope.username = "";
    $scope.message = "";
    $scope.form_inactive = false;
    $scope.waiting = false;

    $scope.login = function() {
        $scope.form_inactive = true;
        $scope.waiting = true;
        $scope.message = "Logger ind...";
        $http.post("/api/usermanager/login", {username:$scope.username, raw_password:$scope.password})
            .success(function(data) {
                $scope.waiting = false;
                $rootScope.logged_in = data.logged_in;
                $rootScope.me = data.user;
                $location.url("/#");
            }).error(function(data) {
                $scope.form_inactive = false;
                $scope.waiting = false;
                switch (data.message) {
                case "invalid username or password":
                    $scope.message = "Forkert brugernavn eller løsen";
                    break;
                case "user deleted":
                    $scope.message = "Din bruger er blevet slettet";
                    break;
                }
            });
        console.log("login request send");
    };

    $scope.forgot = function(form) {
        form.username.$setTouched();
        if (!form.username.$invalid) {
            $http.post("/api/usermanager/password/forgot", {username:$scope.username})
                .success(function(data) {
                    $scope.message = "En email med et genaktiveringslink er blevet sendt til dig.";
                })
                .error(function(data) {
                    switch (data.message) {
                    case "no such user":
                        $scope.message = "Forkert brugernavn";
                        break;
                    case "no email":
                        $scope.message = "Du har ingen tilknyttet email. Kontakt en administrator eller skriv til rkg-listen";
                        break;
                    }
                });
        }
    };
});
