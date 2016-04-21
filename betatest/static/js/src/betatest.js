// OpenCraft -- tools to aid developing and hosting free software projects
// Copyright (C) 2015 OpenCraft <xavier@opencraft.com>
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

(function(){
"use strict";

// App configuration //////////////////////////////////////////////////////////

var app = angular.module('BetaTestApp', ['djng.forms']);

app.config(function($httpProvider) {
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});


// Controllers ////////////////////////////////////////////////////////////////

app.controller('Registration', function($scope, $http, $window, djangoForm) {

    // Validate the registration form on the server
    $scope.validate = _.debounce(function() {
        $http.post('/beta/api/register/validate/', $scope.registration).success(function(errors) {
            djangoForm.setErrors($scope.form, errors);
        }).error(function() {
            console.error('Failed to validate form');
        });
    }, 500);

    // Trigger server-side validation when the user selects a username, to
    // ensure that the username is not already taken
    $scope.$watch('registration.username', function(username) {
        $scope.validate();
    });

});

})();
