// Shorthand for $( document ).ready()
$(function() {
    console.log( "ready!" );
});

function submitClicked() {
    normal_url = "/rating_result?";
    submit(normal_url);
}
function getPDF() {
    pdf_url = "/rating_pdf?";
    submit(pdf_url);
}
function submit(url) {
    var inputs = document.querySelectorAll('input');    
    var myObject = {};
    var submit = "submit"

    for (var i = 0; i < inputs.length; i++) {
        id = inputs[i].id;
        if ( !id.startsWith(submit) ) {
            myObject[id] = inputs[i].value;
            url += id + "=" + encodeURIComponent(inputs[i].value.trim()) + "&";
        }
    }
    url += "industry=" + encodeURIComponent($( "#industry option:selected" ).text().trim());
    window.location.assign(url);
}