var monitorApp = angular.module('monitorApp', []);

monitorApp.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
});

monitorApp.controller('ContainersListCtrl', function($scope) {
    $scope.containers = [
        {'address': 'address 1', 'model': 'en-GB', 'state': 'WORKING'},
        {'address': 'address 2', 'model': 'en-GB', 'state': 'WAITING'},
        {'address': 'address 2', 'model': 'en-GB', 'state': 'READY'},
        {'address': 'address 2', 'model': 'en-GB', 'state': 'NOT RESPONDING'}
    ];
});
