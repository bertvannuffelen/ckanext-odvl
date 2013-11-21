// Dataset map module
this.ckan.module('tag-cloud', function ($$, _) {

  return {

    initialize: function () {
        var $el = this.el
        var counts = []
        $el.find(".tag").each(
            function(idx, tag) {
                counts.push($$(tag).attr("data-count"))
            })
        var min = Math.min.apply(null,counts)
        var max = Math.max.apply(null,counts)
        var delta = max - min

        $el.find(".tag").each(
            function(idx, tag) {
                var rel = delta == 0 ? 100 : 75 + 50 * ($$(tag).attr("data-count") - min) / delta
                $$(tag).css("font-size", rel+"%")
                       //.css("border-radius", 15*rel/100+"px")
            })
        /$el.attr("data-totalcount")

    }

  }
});
