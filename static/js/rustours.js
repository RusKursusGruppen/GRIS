
gris.controller("rustoursCtrl", function($scope, $http, $rootScope, $location) {
    $scope.selected = null;
    $scope.message = "";

    $http.get("/api/rustours")
        .success(function(data) {
            $scope.rustours = data.rustours;
            $scope.years = data.years;
            var id = parseInt(Object.keys($location.search())[0]) || null;
            if (id !== null) {
                $scope.years.forEach(function (year) {
                    $scope.rustours[year].forEach(function (tour) {
                        if (tour.tour_id === id) {
                            $scope.select(tour)
                        }
                    });
                });
                if ($scope.selected === null) {
                    $scope.message = "Den angivne rustur findes ikke";
                }
            }
        });
    $scope.select = function(tour, event) {
        // Deselect tour
        if ($scope.selected === tour) {
            // Don't change url on deselection
            // also prevents opening new tabs when deselecting
            event.preventDefault();
            $location.search($scope.selected.tour_id, null);
            $scope.selected = null;

        } else {
            $scope.selected = tour;
            $location.search(tour.tour_id);
            $http.post("/api/rustours/tour", {tour_id: tour.tour_id})
                .success(function(data) {
                    for (var key in data.tour) {
                        console.log(key);
                        $scope.selected[key] = data.tour[key];
                    }
                    $scope.selected.tutors = data.tutors;
                });
        }

    };
});
