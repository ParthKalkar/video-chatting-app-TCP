if (typeof module === 'object') {window.module = module; module = undefined;}


const ipcRenderer = require('electron').ipcRenderer; 
//send the info to main process . we can pass any arguments as second param.


if (window.module) module = window.module;

function vidImage(element) {
    element.src = element.bln ? "./Images/video-on.svg" : "./Images/video-off.svg";
    element.bln = !element.bln;  /* assigns opposite boolean value always */
    ipcRenderer.send("toggle_vid",!element.bln);
}

function micImage(element) {
    console.log('Changed mic')
    element.src = element.bln ? "./Images/mic-on.svg" : "./Images/mic-off.svg";
    element.bln = !element.bln;  /* assigns opposite boolean value always */
    ipcRenderer.send("toggle_mic",!element.bln);
}

function sendUsername(element){
    let username = document.getElementById('username').value;
    ipcRenderer.send("send_username", username);
    console.log("Username submitted from Renderer!")
}

setInterval(()=>{
    ipcRenderer.send('online_list_request',undefined)
},1000);  // the shorter the more likely it is to miss a click

ipcRenderer.on('online_list',(event,arg)=>{
    let res = ""
    for(var i=0;i<arg.length;i++)
    {
        var name = arg[i]['name'];
        //console.log(name);
        res += `<li>${name}<button class="makecall-home" onclick="make_call(this)" id="${i}">
        <img class="call-button-home"  src="./Images/Make-call.svg" alt=""></button></li>`
    }
    if(res==''){
        res = `<li> Looks like no one is online :( </li>`
    }
    var ls = document.getElementById("online_list");
    ls.innerHTML = res;
});

function make_call(button){
    var id = button.id;
    console.log("Calling id : " + id);
    ipcRenderer.send('make_call', id);
}