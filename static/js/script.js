$(document).ready(function() {
    $('.sidenav').sidenav();
    $(".dropdown-trigger").dropdown();
    $('.parallax').parallax();
    $('select').formSelect();
});

$(document).ready(function() {
    $("#arrow-toggle-down").click(function(){
        $("#chart-toggle").slideToggle("slow");
    });
    $("#chart-toggle").hide();
});

$(document).ready(function() {
    $('select').material_select();

    // for HTML5 "required" attribute
    $("select[required]").css({
        display: "inline",
        height: 0,
        padding: 0,
        width: 0
    });
});