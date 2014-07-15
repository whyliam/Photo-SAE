(function($) {
    $.fn.extend({
        "my_page": function(form) {
            var $this = this;
            var pageinfo = {
                url: $(this).attr("url"),
                currentPage: $(this).attr("currentPage") * 1,
                pageCount: $(this).attr("pageCount") * 1
            };
            if (pageinfo.pageCount < 2) 
                return false;
            var start = 0,
            end = 10;
            if (pageinfo.currentPage >= 10) 
                start = pageinfo.currentPage - 5;
            if (pageinfo.pageCount > pageinfo.currentPage + 5) 
                end = pageinfo.currentPage + 5;
            else 
                end = pageinfo.pageCount;
            var html = [];
            if (pageinfo.currentPage != 1) 
                html.push("<a class='previouspostslink' >前一页</a>");
            if (pageinfo.pageCount > 10 && pageinfo.currentPage > 9) 
                html.push("<a class='page'>1</a>	<span class='extend'>...</span>");
            for (var i = start; i < end; i++) {
                if ((i + 1) < pageinfo.currentPage) 
                    html.push("<a class='page smaller' >" + (i + 1) + "</a>");
                if ((i + 1) == pageinfo.currentPage) 
                    html.push("<a class='current' >" + (i + 1) + "</a>");
                if ((i + 1) > pageinfo.currentPage) 
                    html.push("<a class='page larger' >" + (i + 1) + "</a>	")
            }
            if (pageinfo.pageCount > 10 && pageinfo.currentPage < pageinfo.pageCount - 4) 
                html.push("<span class='extend'>...</span><a class='page'>" + pageinfo.pageCount + "</a>");
            if (pageinfo.currentPage != pageinfo.pageCount) 
                html.push("	<a class='nextpostslink' >后一页</a>");
            $this.html(html.join(""));
            $this.find("a.page").bind("click",
            function() {
                redirectTo($(this).html())
            });
            $this.find("a.previouspostslink").bind("click",
            function() {
                redirectTo(pageinfo.currentPage - 1)
            });
            $this.find("a.nextpostslink").bind("click",
            function() {
                redirectTo(pageinfo.currentPage + 1)
            });
            function redirectTo(jump) {
                var url = pageinfo.url;
                url += "page=" + jump;
                window.location.href = url
            }
            return $this
        }
    })
})(jQuery);