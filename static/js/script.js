$(document).ready(function() {
    $('.sidenav').sidenav();
    $(".dropdown-trigger").dropdown();
    $('.parallax').parallax();
    $('select').formSelect();
    $("#toggle-charts-btn,#arrow-toggle-charts").click(function() {
        $("#chart-toggle").slideToggle("slow");
    });
    $("#toggle-filter,#toggle-filter-arrow").click(function() {
        $("#filter").slideToggle("slow");
    });
    $("#chart-toggle,#filter").hide();
    $('#reset-btn').click(function(){
        $('#reset').val('True');
    });
    // Fix materialize bug. It doesn't display required validation form
    $('select[required]').css({
        display: 'inline',
        position: 'absolute',
        float: 'left',
        padding: 0,
        margin: 0,
        border: '1px solid rgba(255,255,255,0)',
        height: 0,
        width: 0,
        top: '2em',
        left: '3em'
    });
    // Add "Select All" to select materialize form
    $('select').formSelect();
    $('select.select_all').siblings('ul').prepend('<li id=sm_select_all><span>Select All</span></li>');
    $('li#sm_select_all').on('click', function() {
        var jq_elem = $(this),
            jq_elem_span = jq_elem.find('span'),
            select_all = jq_elem_span.text() == 'Select All',
            set_text = select_all ? 'Select None' : 'Select All';
        jq_elem_span.text(set_text);
        jq_elem.siblings('li').filter(function() {
            return $(this).find('input').prop('checked') != select_all;
        }).click();
    });
});
