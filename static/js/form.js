// Shorthand for $( document ).ready()
$(function() {
    console.log( "ready!" );
});

function submitClicked() {
    var inputs = document.querySelectorAll('input');    
    var myObject = {};
    var submitId = "submit_btn"

    url = "/rating_result?";
    for (var i = 0; i < inputs.length; i++) {
        id = inputs[i].id;
        if ( id !== submitId ) {
            myObject[id] = inputs[i].value;
            url += id + "=" + encodeURIComponent(inputs[i].value.trim()) + "&";
        }
    }
    url += "industry=" + encodeURIComponent($( "#industry option:selected" ).text().trim());
    window.location.assign(url);
}