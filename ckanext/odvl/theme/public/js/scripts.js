(function(){

	function init(){

		datatextswap();

		showfiltermap();

		toggletabs();

		removeclamp();

		showmoretable();

		preventdefault();

		onescapeclose();	
	}

	/**
    * Switch text on a label (eg: show -> hide)
    */
	function datatextswap(){
		var elements = document.getElementsByClassName('js-text-swap');

		[].forEach.call(elements, function(element) {

	        element.addEventListener('click', function(e) {

	          e.preventDefault();

			  if (element.getAttribute("data-text-swap") == element.innerHTML) {
			    element.innerHTML = element.getAttribute("data-text-original");
			  } else {
			    element.setAttribute("data-text-original", element.innerHTML);
			    element.innerHTML = element.getAttribute("data-text-swap");
			  }
			}, false);

	    });
	}


	/**
    * Show filter map
    */
	function showfiltermap(){
		var elements = document.getElementsByClassName('js-scroll-to-button');

		[].forEach.call(elements, function(element) {

	        element.addEventListener('click', function(e) {

	        	e.preventDefault();

	        	toggleClass(document.getElementById('enlarge-button'), 'js-scroll-to-button--active');

	        	var scroll_to_element = document.getElementsByClassName(element.getAttribute("data-scroll-to"))[0];

	        	toggleClass(scroll_to_element, 'js-scroll-to--active');
				scrollTo(document.body, scroll_to_element.offsetTop, 600);
			}, false);

	    });
	}


	/**
    * Show a div
    */
	function showdiv(){
		var elements = document.getElementsByClassName('js-show-div-button');

		[].forEach.call(elements, function(element) {

	        element.addEventListener('click', function(e) {

	        	e.preventDefault();

	        	var target = document.getElementsByClassName(element.getAttribute("data-show-div"))[0];
	        	toggleClass(target, 'js-show-div--active');
				scrollTo(document.body, scroll_to_element.offsetTop, 600);
			}, false);

	    });
	}


	/**
    * Show more of table
    */
	function showmoretable(){
		var elements = document.getElementsByClassName('js-table-more-button');

		[].forEach.call(elements, function(element) {

	        element.addEventListener('click', function(e) {

	        	e.preventDefault();

	        	var table = document.getElementsByClassName('js-table')[0];
				removeClass(table, 'table--items-clamp');

				element.parentNode.removeChild(element);

			}, false);

	    });
	}


	/**
    * Remove Clamp function
    * .js-remove-clamp-button heeft data-clamp-remove-id attribuut
    * [data-clamp] heeft data-clamp-id attribuut
    * .js-remove-clamp-button & Data-clamp moeten dezelfde data-clamp-id hebben (eg: 1)
    */
	function removeclamp(){
		var elements = document.getElementsByClassName('js-remove-clamp-button');

		[].forEach.call(elements, function(element) {

	        element.addEventListener('click', function(e) {

	        	e.preventDefault();

	        	var clampedText = element.getAttribute('data-clamp-remove-id');
	        	var targets = document.getElementsByClassName('data-clamp-remove-target');

	        	[].forEach.call(targets, function(target){
	        		if (target.getAttribute('data-clamp-id') === clampedText) {
	        			target.removeAttribute('data-clamp');
	        			clamp(target, 9999);
	        			removeClass(target, 'js-clamped');
	        		}
	        	}, false);

	        	element.parentNode.removeChild(element);

			}, false);

	    });
	}

	/**
    * Toggle tabs
    */
	function toggletabs(){

		var elements = document.getElementsByClassName('js-toggle-tabs-button');

		[].forEach.call(elements, function(element) {

	        element.addEventListener('click', function(e) {

	        	e.preventDefault();

	        	//Remove all active classes from tabs
	        	[].forEach.call(elements, function(els){
	        		removeClass(els.parentNode, 'tab--active');
	        	});

	        	addClass(element.parentNode, 'tab--active');

	        	//Remove active class from all tabs except for the active one
	        	var clickedTab = element.getAttribute('data-toggle-tabs-target');
	        	var tabs = document.getElementsByClassName('js-toggle-tabs--tab');
	        	
	        	[].forEach.call(tabs, function(tab){
	        		if (tab.getAttribute('data-toggle-tabs-anchor') === clickedTab) {
	        			addClass(tab, 'js-toggle-tabs--active');
	        		}else{
	        			removeClass(tab, 'js-toggle-tabs--active');
	        		}
	        	});

			}, false);

	    });
	}

	/**
    * On escape close all js-popups
    */
	function onescapeclose(){
		window.onkeydown = function( event ) {
		    if ( event.keyCode === 27 ) {
		        var elements = document.querySelectorAll('.js-popup--open');
		        [].forEach.call(elements, function(element){
		        	removeClass(element, 'js-popup--open');
		        });
		    }
		};
	}


	/**
    * Scroll to target snippet
    */
	function scrollTo(element, to, duration) {
	    var start = element.scrollTop,
	        change = to - start,
	        increment = 20;

	    var animateScroll = function(elapsedTime) {        
	        elapsedTime += increment;
	        var position = easeInOut(elapsedTime, start, change, duration);                        
	        element.scrollTop = position; 
	        if (elapsedTime < duration) {
	            setTimeout(function() {
	                animateScroll(elapsedTime);
	            }, increment);
	        }
	    };

	    animateScroll(0);
	}


	/**
    * Prevent default function
    */
	function preventdefault(){
		var elements = document.getElementsByClassName('js-preventdefault');

		[].forEach.call(elements, function(element) {

	        element.addEventListener('click', function(e) {
	          e.preventDefault();
			}, false);

	    });
	}

	/**
    * Easing snippet
    */
	function easeInOut(currentTime, start, change, duration) {
	    currentTime /= duration / 2;
	    if (currentTime < 1) {
	        return change / 2 * currentTime * currentTime + start;
	    }
	    currentTime -= 1;
	    return -change / 2 * (currentTime * (currentTime - 2) - 1) + start;
	}




	// closest polyfill
	function closest(el, selector) {
	  var matchesFn;

	  // find vendor prefix
	  ['matches','webkitMatchesSelector','mozMatchesSelector','msMatchesSelector','oMatchesSelector'].some(function(fn) {
	    if (typeof document.body[fn] == 'function') {
	      matchesFn = fn;
	      return true;
	    }
	    return false;
	  })

	  // traverse parents
	  while (el!==null) {
	    parent = el.parentElement;
	    if (parent!==null && parent[matchesFn](selector)) {
	      return parent;
	    }
	    el = parent;
	  }

	  return null;
	}


	//Trigger event on element
	function fireEvent(element,event) {
	   if (document.createEvent) {
	       // dispatch for firefox + others
	       var evt = document.createEvent("HTMLEvents");
	       evt.initEvent(event, true, true ); // event type,bubbling,cancelable
	       return !element.dispatchEvent(evt);
	   } else {
	       // dispatch for IE
	       var evt = document.createEventObject();
	       return element.fireEvent('on'+event,evt)
	   }
	}

	init();

})();