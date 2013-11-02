// Dataset map module
this.ckan.module('tag-cloud', function ($$, _) {

  return {

    initialize: function () {
        var $el = this.el
        $el.find(".tag").each(
            function(idx, tag) {
                var rel=$$(tag).attr("data-count")/$el.attr("data-totalcount")
                $$(tag).css("font-size", rel*100+"%")

            })
    }

  }
});
