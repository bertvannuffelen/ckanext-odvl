// Dataset map module
this.ckan.module('vl-breadcrumb', function ($$, _) {

    return {

        initialize: function () {

            var $el = this.el

            var navtabs = {}
            $el.find("#navigation_tabs>li>a").each(
                function(idx, anchor) {
                    var $a = $(anchor)
                    navtabs[$a.attr('href')] = $a.text()
                })

            var levels = []
            $el.find("#breadcrumb_content>li>a").each(
                function(idx, anchor) {
                    var $a = $(anchor)
                    var newLevel = {}

                    if (levels.length == 0) {
                        newLevel = {
                            type:'menu',
                            "showAsLink": true,
                            "sections": [
                                $.map(navtabs, function(label, href) {
                                    return {
                                        "label": label,
                                        "url": href,
                                        "highlight": $a.attr('href') == href
                                    }
                                })

                            ]
                        }
                        if (!navtabs[$a.attr('href')]) {
                            newLevel.sections.push([
                                {
                                    "label": $a.text(),
                                    "url": $a.attr('href'),
                                    "highlight": true
                                }]
                            )
                        }
                    } else {
                        newLevel =
                            {"type": "link",
                            "label": $a.text(),
                            "url": $a.attr('href')}
                    }

                    levels.push( newLevel )
                })

            // Ensure the WidgetApi.Event.Handlers namespace exists.
            window.WidgetApi = window.WidgetApi || {};
            window.WidgetApi.Event = window.WidgetApi.Event || {};
            window.WidgetApi.Event.Handlers = window.WidgetApi.Event.Handlers || [];

            // Register for the "WidgetCreated" event.
            window.WidgetApi.Event.Handlers.push({
                "event": "WidgetAttached",
                "data": null,
                "handler": function (e) {
                    // Get the widget which was created.
                    var widget = e.getEventArgs().getSource();
                    // Check whether widget is a global header.
                    if (widget.getClassName() === 'FlemishAuthorities.InfolijnWidget.GlobalHeader') {
                        // Configure the breadcrumb.
                        var breadcrumb = widget.getBreadcrumb();
                        // Set the breadcrumb level definitions.
                        breadcrumb.getLevels().addMultiple(levels);

                        // Configure the search.
                        widget.setSearchConfig('GET', '/dataset', 'q', 'Zoek');
                    }
                }
            });

        }

    }
});


/*[
 {
 "type": "menu",
 "showAsLink": true,
 "sections": [
 [
 {
 "label": "Test 1",
 "url": "http://www.google.be",
 "highlight": true
 },
 {
 "label": "Test 2",
 "url": "http://www.google.be"
 },
 {
 "label": "Test 3",
 "url": "http://www.google.be",
 "target": "_blank"
 },
 {
 "label": "Test 4",
 "url": "http://www.google.be"
 },
 {
 "label": "Test 5",
 "url": "http://www.google.be"
 }
 ],
 [
 {
 "label": "Test 6",
 "url": "http://www.google.be"
 }
 ]
 ]
 },
 {
 "type": "menu",
 "showAsLink": false,
 "sections": [
 [
 {
 "label": "Test 1",
 "url": "http://www.google.be"
 },
 {
 "label": "Test 2",
 "url": "http://www.google.be"
 },
 {
 "label": "Test 3",
 "url": "http://www.google.be",
 "target": "_blank",
 "highlight": true
 },
 {
 "label": "Test 4",
 "url": "http://www.google.be"
 },
 {
 "label": "Test 5",
 "url": "http://www.google.be"
 }
 ],
 [
 {
 "label": "Test 6",
 "url": "http://www.google.be"
 }
 ]
 ]
 },
 {
 "type": "link",
 "label": "Lorem ipsum 1",
 "url": "http://www.google.be",
 "target": "_blank"
 },
 {
 "type": "text",
 "label": "Pagina"
 },
 ]
    */