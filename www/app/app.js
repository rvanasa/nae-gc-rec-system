/* global angular */
angular.module('app', ['ui.bootstrap'])

.component('app', {
	templateUrl: 'component/app.html',
	controller(Storage, UserSchema)
	{
		var $ctrl = this;
		
		$ctrl.userSchema = UserSchema;
		
		$ctrl.user = Storage.load('user') || {};
		$ctrl.saveUser = function()
		{
			Storage.save('user', $ctrl.user);
		}
		
		$ctrl.page = Storage.load('page') || 'user';
		$ctrl.setPage = function(page)
		{
			$ctrl.page = page;
			Storage.save('page', $ctrl.page);
		}
		
		$ctrl.problem = {
			id: '12345',
			text: 'What color are leaves?',
			options: [{
				id: 'A',
				text: 'Green',
			}, {
				id: 'B',
				text: 'Red',
			}, {
				id: 'C',
				text: 'Black',
			}, {
				id: 'D',
				text: 'White',
			}, {
				id: 'E',
				text: 'Depends?',
			}],
		};
		
		$ctrl.submit = function()
		{
			$ctrl.problem.response = {
				correct: 'E',
			};
		}
		
		$ctrl.nextQuestion = function()
		{
			$ctrl.problem.selected = null;
			$ctrl.problem.response = null;
		}
	}
})

.component('formValue', {
	templateUrl: 'component/form-value.html',
	bindings: {
		schema: '<',
		model: '=',
		change: '&',
	},
	controller($timeout)
	{
		var $ctrl = this;
		
		$ctrl.schemaValues = Array.isArray($ctrl.schema) ? $ctrl.schema : $ctrl.schema.schema;
		
		$ctrl.type = $ctrl.schema.type || 'text';
		
		$ctrl.onChange = function()
		{
			$timeout(() => $ctrl.change());
		}
	}
})

.factory('API', function()
{
	
})

.factory('Storage', function($window)
{
	return {
		load(key)
		{
			var data = $window.localStorage.getItem(key);
			if(data) return JSON.parse(data);
		},
		save(key, data)
		{
			$window.localStorage.setItem(key, data != null ? JSON.stringify(data) : '');
		},
	};
})

.value('UserSchema', [{
	id: 'name',
	name: 'Name',
}, {
	id: 'prefs',
	name: 'Preferences',
	schema: [{
		id: 'grade',
		name: 'Grade',
		type: 'tel',
	}, {
		id: 'state',
		name: 'State',
		options: ['Alaska', 'California', 'Colorado'],
	}],
}])