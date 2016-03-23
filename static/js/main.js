var dc = 1;

function getDc() {
    return dc;
}

$(document).ready(function() {
    var table = $('#vm').DataTable( {
        "processing": true,
        "serverSide": false,
        "ajax": {
            "url": "/getservers",
            "type": "GET"
        },
        "columns": [
            {'data': 'name'},
            {'data': 'type'},
            {'data': 'ip'},
            {'data': 'actions'},
            {'data': 'state'}
        ]
    } );

    $('#datacenter_text_id').text(dc);

    $('#dc_selector').find('li').bind("click", function(e) {
       table.ajax.url( '/getservers?dc=' + $(this).attr('id') ).load();
        console.log("Table Reloaded.");
        dc = $(this).attr('id');
        $('#datacenter_text_id').text(dc);
    });

    $('body').on('click', '#vm tbody tr td button', function () {
        var action = $(this).attr('id');
        var vm_id = $(this).closest('tr').attr('id');
        $.post('/action', {action: action, vm_id: vm_id, dc: dc})
            .done(function(data) {
                alert('Action Enqueued.');
            })
    });

    $("#submit_create").on('click', function () {
        var serialized_json = $("#formCreation").serialize();
        serialized_json += "&dc=" + encodeURIComponent(getDc());
        $.post('/create_smart', serialized_json)
            .done(function() {
                alert("Creation Enqueued");
            });
    });
} );
