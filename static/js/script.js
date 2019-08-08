$(document).ready(function() {
    $('.sidenav').sidenav();
    $(".dropdown-trigger").dropdown();
    $('.parallax').parallax();
    $('select').formSelect();
    $("#arrow-toggle-down").click(function(){
        $("#chart-toggle").slideToggle("slow");
    });
    $("#chart-toggle").hide();
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
});
