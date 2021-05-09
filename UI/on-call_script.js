if (typeof module === 'object') {window.module = module; module = undefined;}


const ipcRenderer = require('electron').ipcRenderer; 
//send the info to main process . we can pass any arguments as second param.


if (window.module) module = window.module;


//checking the status of video and audio

var cam = document.getElementById('vid-on-talking');
var mic = document.getElementById('mic-on-talking'); // will come back here later

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

function finishCall() {
    console.log("Call ended.");
    ipcRenderer.send("call_finish", undefined);
}