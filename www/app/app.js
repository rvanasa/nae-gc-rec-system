/* global angular */
angular.module('app', ['ui.bootstrap'])

.component('app', {
	templateUrl: 'component/app.html',
	controller(API, Storage, UserSchema)
	{
		var $ctrl = this;
		
		$ctrl.userSchema = UserSchema;
		
		$ctrl.user = Storage.load('user') || {id: '12345'};
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
		
		$ctrl.nextQuestion = function()
		{
			API.getQuestion($ctrl.user)
				.then(problem => $ctrl.problem = problem);
		}
		$ctrl.nextQuestion();
		
		$ctrl.submit = function()
		{
			API.submitAnswer($ctrl.user, $ctrl.problem.selected)
				.then(result => $ctrl.problem.result = result);
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
		
		if($ctrl.schemaValues) $ctrl.type = 'schema';
		else if($ctrl.schema.options) $ctrl.type = 'select';
		else $ctrl.type = $ctrl.schema.type || 'text';
		
		$ctrl.onChange = function()
		{
			$timeout(() => $ctrl.change());
		}
	}
})

.factory('API', function($http)
{
	return {
		getQuestion(user)
		{
			return wrap($http.get('/api/question' + getQueryString({user: user.id})));
		},
		submitAnswer(user, selected)
		{
			return wrap($http.post('/api/answer' + getQueryString({user: user.id, selected})));
		},
	};
	
	function getQueryString(map)
	{
		return '?' + Object.keys(map).map(key => encodeURIComponent(key) + '=' + encodeURIComponent(map[key])).join('&');
	}
	
	function wrap(promise)
	{
		return promise.then(res => res.data);
	}
})

.factory('Storage', function($window)
{
	return {
		load(key)
		{
			var value = $window.localStorage.getItem(key);
			if(value) return JSON.parse(value);
		},
		save(key, value)
		{
			$window.localStorage.setItem(key, value != null ? JSON.stringify(value) : '');
		},
	};
})

.value('UserSchema', [{
	id: 'id',
	name: 'User ID',
}, {
	id: 'name',
	name: 'Name',
}, {
	id: 'prefs',
	name: 'Preferences',
	schema: [{
		id: 'grade',
		name: 'Grade',
		type: 'number',
	}, {
		id: 'state',
		name: 'State',
		options: ['Alaska', 'California', 'Colorado'],
	}],
}])