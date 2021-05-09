
function vidImage(element) {
    element.src = element.bln ? "./Images/Video-On.svg" : "./Images/Video-Off.svg";
    element.bln = !element.bln;  /* assigns opposite boolean value always */
}

function micImage(element) {
    element.src = element.bln ? "./Images/Mic-On.svg" : "./Images/Mic-Off.svg";
    element.bln = !element.bln;  /* assigns opposite boolean value always */
}