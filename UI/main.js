const electron = require('electron');
const url = require('url');
const path = require('path');
let {PythonShell} =  require('python-shell');
let backend = require(path.join(__dirname, 'backend_api.js'))


const{app, dialog, BrowserWindow, ipcMain} = electron;
let mainwindow;
let addWindow;


console.log("Hello from before the app is ready")

// Listen for the app to be ready
app.on('ready', function(){
    // Create new window
    mainwindow = new BrowserWindow({
        frame: true,
        webPreferences: {
        nodeIntegration: true,
        webSecurity: false,
    	plugins: true
      } 
    });
    mainwindow.maximize()
    mainwindow.removeMenu()
    //mainWindow.webContents.openDevTools()
    // Load the first HTML file in the window
    mainwindow.loadURL(url.format({
        pathname: path.join(__dirname, 'home.html'),
        protocol:'file:', 
        slashes: true
}));


    // Quit app when closed
    mainwindow.on('closed', function(){
        backend.quit();
        app.quit();
    })
});

console.log("Hello after the app got ready")

ipcMain.on("send_username", (event, arg)=>{
    console.log(arg)
});

// Handle create add window
function createAddWindow(){
     // Create new window
     addWindow = new BrowserWindow({
         title: 'Calling'

     });
     // Load the second HTML file in the window
     addWindow.loadURL(url.format({
         pathname: path.join(__dirname, 'screen2.html'),
         protocol:'file:', 
         slashes: true
 }));

    // Garbage collection handle
    addWindow.on('close', function(){
        addWindow = null;
    });

}

function vidImage(element) {
    element.src = element.bln ? "./Images/video-on.svg" : "./Images/video-off.svg";
    element.bln = !element.bln;  /* assigns opposite boolean value always */
}

function micImage(element) {
    console.log('Changed mic')
    element.src = element.bln ? "./Images/mic-on.svg" : "./Images/mic-off.svg";
    element.bln = !element.bln;  /* assigns opposite boolean value always */
}

function sendUsername(element){
    let username = document.getElementById('username').value;
    console.log(username)
    backend.submit_username(username.value);
    console.log("Called!")
}

/*document.getElementById('username').addEventListener('click', function(){
    let username = document.getElementById('username').value;
    console.log(username)
    backend.submit_username(username.value);
})*/

// For now we have problems with pyshell

/*let pyshell = new PythonShell('../Core/main.py')
console.log("Wiiiiouw")
    pyshell.on("message", function(message) {
        console.log(message)
      });

pyshell.end(function (err) {
        if (err) throw err;
        console.log('finished');
  });*/
