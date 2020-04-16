$(document).ready(function () {
    draw_table()
});

function draw_table() {
    $('#table_body').html('');
    $.getJSON('http://127.0.0.1:5000/get_all', function (data) {
        $.each(data, function (key, val) {
            let row = "";
            $.each(val, function (key, val) {
                let new_val = "";
                if (key === "id") {
                    return;
                } else if (key === "href") {
                    new_val = '<a href=\"' + val + '\">Click</a>';
                } else if (key.startsWith("picture")) {
                    new_val = '<img src="' + val + '" alt="Picrelated" width="200" height="267">';
                } else {
                    new_val = val;
                }
                row += '<td>' + new_val + '</td>';
            });
            $('#table_body').append('<tr>' + row + '</tr>');
        });
    });
}
