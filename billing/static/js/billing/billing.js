// OpenCraft -- tools to aid developing and hosting free software projects
// Copyright (C) 2015-2017 OpenCraft <contact@opencraft.com>
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

// App configuration //////////////////////////////////////////////////////////

var app = angular.module('OpenCraftApp');
app.requires.push('restangular');

app.config(function(RestangularProvider) {
    RestangularProvider.setRequestSuffix('/');
});


// Services ///////////////////////////////////////////////////////////////////

app.factory('OpenCraftAPI', function(Restangular) {
    return Restangular.withConfig(function(RestangularConfigurer) {
        RestangularConfigurer.setBaseUrl('/api/v1');
    });
});


// Controllers ////////////////////////////////////////////////////////////////

app.controller('PaymentMethodSelection', ['$scope', '$attrs', 'OpenCraftAPI',
    function($scope, $attrs, OpenCraftAPI) {

        var stripeHandler;

        $scope.init = function() {
            $scope.init_stripe();
        };

        $scope.init_stripe = function() {
            $scope.updateBillingCustomer().then(function() {
                stripeHandler = StripeCheckout.configure({
                    key: $scope.billingCustomer.stripe_public_key,
                    name: "Open edX Hosting",
                    token: function(token, args) {
                        console.log("Got stripe token: " + token.id);
                        $scope.setStripeToken(token);
                    }
                })

                // Automatically launch the checkout if we don't have a card recorded
                angular.element(document).ready(function () {
                    if (!$scope.billingCustomer.stripe_customer_id) {
                        $scope.doCheckout();
                    }
                });
            });
        };

        $scope.doCheckout = function() {
            var options = {
                billingAddress: true,
                amount: 0,
                currency: 'EUR',
                email: $scope.$eval($attrs.ocEmail)
            };

            if ($scope.billingCustomer.stripe_customer_id) {
                options.description = 'Update billing information';
                options.panelLabel = 'Update card';
            } else {
                options.description = '1 month of free trial, then ' +
                                      $scope.billingCustomer.instance_base_monthly_price/100 + '€/month';
                options.panelLabel = 'Start Free Trial';
            }

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

        $scope.init();
    }
]);

})();
