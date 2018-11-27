
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

displayCsv = function(facet) {
    CsvToHtmlTable.init({
        csv_path: '/summary/'+facet+'.csv',
        element: 'stat-table-container',
        allow_download: true,
        csv_options: {separator: ',', delimiter: '"'},
        datatables_options: {
            "paging": true,
            "order": [[ 1, "desc" ]] ,
            "columnDefs": [ {
                "targets": 0,
                "render": function ( data, type, row, meta ) {
                    return '<div class="stat_cell" title="'+escapeHtml(data)+'">'+escapeHtml(data)+'</a>';
                }
            } ]
        }
    });
}

displayCsv('org');