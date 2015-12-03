var transcript = function() {
    var target = document.getElementById("targetLocation");

    target.appendChild(document.createTextNode("HELLO"));
}

var clearBox = function(elementID) {
    document.getElementById(elementID).innerHTML = "";
}
