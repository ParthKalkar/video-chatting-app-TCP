if (typeof module === 'object') {window.module = module; module = undefined;}


const ipcRenderer = require('electron').ipcRenderer; 
//send the info to main process . we can pass any arguments as second param.


if (window.module) module = window.module;

//checking the status of video and audio

var cam = document.getElementById('vid-on-calling');
var mic = document.getElementById('mic-on-calling'); // will come back here later

ipcRenderer.send('use_video_request',undefined);
ipcRenderer.send('use_audio_request',undefined);

ipcRenderer.on('use_video', (event,data)=>{
    if(data){
        cam.src = "./Images/video-on.svg";
        mic.bln = false;
    }
    else{
        cam.src = "./Images/video-off.svg";
        mic.bln = true;
    }
});


ipcRenderer.on('use_audio', (event,data)=>{
    if(data){
        mic.src = "./Images/mic-on.svg";
        mic.bln = false;
    }
    else{
        mic.src = "./Images/mic-off.svg";
        mic.bln = true;
    }
});

setInterval(()=>{
    ipcRenderer.send("correspondent_name_request", undefined);
}, 700);

ipcRenderer.on("correspondent_name", (event,arg)=>{
    var title = document.getElementById('call_title');
    title.innerHTML= `Calling ${arg} ...`;
});

//toggling video and audio
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

function cancelCall() {
    console.log("Call cancelled.");
    ipcRenderer.send("call_cancel", undefined);
}

//remind main to check if the call is accepted
setInterval(()=>{
    ipcRenderer.send("call_accepted_request",undefined);
}, 200);