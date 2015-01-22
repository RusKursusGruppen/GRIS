var login = angular.module("login", []);

login.controller("loginCtrl", function($scope, $http) {
    $scope.login = function() {};
    $scope.username = "";
    $scope.username = "";

    $scope.message = "";

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
    }
});
