
function submitClicked() {
    var list = [];
    url = "/rating_result?";
    for(i = 1; i <= 20; i++) {
        var num = ("0" + i).slice(-2);
        elem_id = "finarg" + num;
        url += "arg=" + (document.getElementById(elem_id).value || "0") + "&";
    }
    url += "arg=1";
    window.location.assign(url);
}