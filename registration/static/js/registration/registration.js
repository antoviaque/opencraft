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

(function() {
'use strict';

// iCheck /////////////////////////////////////////////////////////////////////

// https://github.com/fronteed/iCheck/
$(document).ready(function() {
    $('input').icheck({
        checkboxClass: 'checkbox',
        hoverClass: 'checkbox--hover',
        focusClass: 'checkbox--focus',
        checkedClass: 'checkbox--checked',
        activeClass: 'checkbox--active',
        handle: 'checkbox'
    });
});


// App configuration //////////////////////////////////////////////////////////

var app = angular.module('RegistrationApp', ['djng.forms', 'restangular']);

app.config(function($httpProvider, RestangularProvider) {
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    RestangularProvider.setRequestSuffix('/');
});


// Services ///////////////////////////////////////////////////////////////////

app.factory('OpenCraftAPI', function(Restangular) {
    return Restangular.withConfig(function(RestangularConfigurer) {
        RestangularConfigurer.setBaseUrl('/api/v1');
    });
});


// Controllers ////////////////////////////////////////////////////////////////

app.controller('Registration', ['$scope', '$http', 'djangoForm', 'OpenCraftAPI',
    function($scope, $http, djangoForm, OpenCraftAPI) {

        var stripeHandler;

        $scope.init = function() {
            $scope.init_form();
            $scope.init_stripe();
        };

        $scope.init_form = function() {
            // These fields will be validated on the server via ajax:
            // - Unique checks can only be done on the server.
            var serverValidationFields = [
                'subdomain',
                'username',
                'email',
                'password_confirmation'
            ];

            // Validate password strength
            $scope.$watch('registration.password', function() {
                var validationFeedback = $scope.getValidationFeedback();
                if (validationFeedback) {
                    $scope.displayErrors({ password: validationFeedback });
                }
            });

            // Trigger server-side validation.
            serverValidationFields.forEach(function(field) {
                $scope.$watch('registration.' + field, _.debounce(function() {
                    var formField = $scope.form[field];
                    if (formField && formField.$dirty && formField.$valid) {
                        $scope.validate();
                    }
                }, 500));
            });
        };

        $scope.init_stripe = function() {
            // TODO: Move key to config
            stripeHandler = StripeCheckout.configure({
                key: 'pk_test_dXfAk69u10kOnoAErjfMOSDC',
                name: "Open edX Hosting",
                token: function(token, args) {
                    console.log("Got stripe token: " + token.id);
                    $scope.setStripeToken(token);
                }
            });

            $scope.updateBillingCustomer();

            // Automatically launch the checkout upon successful processing the form
            angular.element(document).ready(function () {
                if ($scope.form['pk'].$viewValue) {
                    $scope.doCheckout();
                }
            });
        };

        $scope.doCheckout = function() {
            // TODO: Move price to config
            var options = {
                description: "1x Starter Instance (monthly)",
                billingAddress: true,
                amount: 9500,
                currency: 'EUR',
                email: $scope.form['email'].$viewValue
            };
            stripeHandler.open(options);
        };

        $scope.updateBillingCustomer = function() {
            return OpenCraftAPI.all("billing/customer").getList().then(function(billingCustomerList) {
                $scope.billingCustomer = billingCustomerList[0];
                console.log('Updated BillingCustomer:', $scope.billingCustomer);
            }, function(response) {
                console.error('Error from server: ', response);
            });
        };

        $scope.setStripeToken = function(token) {
            OpenCraftAPI.all("billing/customer").post({stripe_token: token.id}).then(
                function(billingCustomer) {
                    $scope.billingCustomer = billingCustomer;
                    console.log('Updated BillingCustomer:', $scope.billingCustomer);
                    // TODO: Warn user in the UI
                }, function(response) {
                    console.error('Error from server: ', response);
                    // TODO: Warn user in the UI
                }
            );
        };

        // Returns a list of all form fields.
        $scope.getFormFields = function() {
            return _.keys($scope.form).filter(function(key) {
                return !/^\$/.test(key);
            });
        };

        // Returns current password or undefined:
        // If an existing user accesses the registration form, password fields are not displayed.
        $scope.getPassword = function() {
            var passwordField = $scope.form.password;
            if (passwordField) {
                return passwordField.$viewValue;
            }
            return '';
        };

        // Returns the result of validating current password using zxcvbn.
        $scope.validatePassword = function() {
            var password = $scope.getPassword();
            if (password) {
                var result = zxcvbn(password);
                // Update password strength field
                document.getElementById('id_password_strength').value = result.score;
                return result;
            }
            return {};
        };

        // Returns list of suggestions extracted from password validation result.
        $scope.compileSuggestions = function(validationResult) {
            var suggestions = validationResult.feedback.suggestions,
                warning = validationResult.feedback.warning;
            if (warning) {
                suggestions.push(warning);
            }
            if (_.isEmpty(suggestions)) {
                // zxcvbn did not produce any feedback for current password,
                // so fall back on generic error message
                suggestions.push(
                    'Please use a stronger password: avoid common patterns ' +
                        'and make it long enough to be difficult to crack.'
                );
            }
            return suggestions;
        };

        // Makes sure each suggestion ends with period.
        $scope.formatSuggestions = function(suggestions) {
            return _.map(suggestions, function(suggestion) {
                if (!suggestion.endsWith('.')) {
                    return suggestion + '.';
                }
                return suggestion;
            });
        };

        // Returns feedback from password validation.
        $scope.getValidationFeedback = function() {
            var validationResult = $scope.validatePassword();
            if (validationResult && validationResult.score < 2) {
                var suggestions = $scope.formatSuggestions($scope.compileSuggestions(validationResult));
                // Concatenate suggestions to ensure that all of them are displayed
                return [suggestions.join(" ")];
            }
            return [];
        };

        // Display the given error messages. Due to bugs in django-angular, we must
        // ensure that only modified fields that have passed client-side validation
        // and fields with a $message (i.e.  fields that have already been passed
        // to setErrors) are passed to setErrors.
        // https://github.com/jrief/django-angular/pull/260
        $scope.displayErrors = function(errors) {
            var fields = $scope.getFormFields().filter(function(key) {
                var field = $scope.form[key];
                return field.$message || (field.$dirty && field.$valid);
            });
            errors = _.pick(errors, fields);
            djangoForm.setErrors($scope.form, errors);
        };

        // Validate the registration form on the server.
        $scope.validate = function() {
            var params = {};
            $scope.getFormFields().forEach(function(key) {
                params[key] = $scope.form[key].$viewValue;
            });
            // Ensure that server doesn't validate password strength;
            // it should only do this when user submits the form.
            delete params.password_strength;
            var request = $http.get('/api/v1/registration/register/validate/', {
                params: params
            });
            request.success($scope.displayErrors);
            request.error(function() {
                console.error('Failed to validate form');
            });
        };

        $scope.init();
    }
]);

})();
