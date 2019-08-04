$(document).ready(function() {
    $('.sidenav').sidenav();
    $(".dropdown-trigger").dropdown();
    $('.parallax').parallax();
    $('select').formSelect();
    $("#arrow-toggle-down").click(function(){
        $("#chart-toggle").slideToggle("slow");
    });
    $("#chart-toggle").hide();
});
