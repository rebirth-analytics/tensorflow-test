// Shorthand for $( document ).ready()
$(function() {
    console.log( "ready!" );
});

function submitClicked() {
    var list = [];
    url = "/rating_result?";
    for(i = 1; i <= 20; i++) {
        var num = ("0" + i).slice(-2);
        elem_id = "#finarg" + num;
        url += "arg=" + ($(elem_id).value || "0") + "&";
    }
    var sum = 0;
    $("select.swquestion :selected").each(function() {
        sum += parseInt(this.value);
    });
    url += "arg=1&compliance=" + sum.toString();
    window.location.assign(url);
}