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

    // Validate the registration form on the server. If an array of fields is
    // given, error messages will only be displayed for those fields.
    $scope.validate = _.debounce(function(fields) {
        $http.post('/beta/api/register/validate/', $scope.registration).success(function(errors) {
            if (fields != null) {
                errors = _.pick(errors, fields);
            }
            djangoForm.setErrors($scope.form, errors);
        }).error(function() {
            console.error('Failed to validate form');
        });
    }, 500);

    // Trigger server-side validation when the user selects a username, to
    // ensure that the username is not already taken.
    $scope.$watch('registration.username', function(username) {
        if ($scope.form.$dirty) {
            $scope.validate(['username']);
        }
    });

    // Check that passwords match.
    $scope.$watchGroup(['registration.password', 'registration.password_confirmation'], function(passwords) {
        if (_.all(passwords) && passwords[0] !== passwords[1]) {
            djangoForm.setErrors($scope.form, {
                'password_confirmation': ["The two password fields didn't match."]
            });
        }
    });

    // Check that the password is strong enough.
    $scope.$watch('registration.password', function(password) {
        if (password && zxcvbn(password).score < 2) {
            djangoForm.setErrors($scope.form, {
                'password': ['Please use a stronger password.']
            });
        }
    });

});

})();
