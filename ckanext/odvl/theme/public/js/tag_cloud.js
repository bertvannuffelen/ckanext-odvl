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
                var relPos = delta == 0 ? 0.5 : ($$(tag).attr("data-count") - min) / delta
                var relSize = 75 + 50 * relPos
                //$$(tag).css("font-size", relSize+"%")
                       //.css("border-radius", 15*rel/100+"px")
                $$(tag).parent().toggleClass('tags-list-item__size-'+ (Math.round(relPos * 3)+1), true)
            })
        /$el.attr("data-totalcount")

    }

  }
});
