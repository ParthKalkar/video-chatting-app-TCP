if (typeof module === 'object') {window.module = module; module = undefined;}


const ipcRenderer = require('electron').ipcRenderer; 
//send the info to main process . we can pass any arguments as second param.


if (window.module) module = window.module;


function acceptCall(){
    ipcRenderer.send("accept_call", true);
}

function declineCall(){
    ipcRenderer.send("accept_call", false);
}