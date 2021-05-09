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
        //frame: true,
        webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
        //preload: path.join(__dirname, 'home_script.js')
        //webSecurity: false,
    	//plugins: true
      } 
    });
    mainwindow.maximize()
    //mainwindow.removeMenu()
    
    // Load the first HTML file in the window
    mainwindow.loadURL(url.format({
        pathname: path.join(__dirname, 'home.html'),
        protocol:'file:', 
        slashes: true
}));

    //mainWindow.webContents.openDevTools()
    // Quit app when closed
    mainwindow.on('closed', function(){
        backend.quit();
        app.quit();
    })

    ipcMain.on("make_call", (event,id)=>{
        console.log("Making call to : " + id);
        backend.client.set("correspondent_id", id);
        backend.client.set("status","calling");
        mainwindow.loadURL(url.format({
            pathname: path.join(__dirname, 'calling.html'),
            protocol:'file:', 
            slashes: true
        }));
    });
});


// Listeners for IPC from Renderer


ipcMain.on("send_username", (event, arg)=>{
    console.log("send_username ! "+ arg)
    backend.submit_username(arg)
});

ipcMain.on("toggle_mic", (event, arg)=>{
    if(arg){
        backend.audio_on()
    }
    else {
        backend.audio_off()
    }
});

ipcMain.on("toggle_vid", (event, arg)=>{
    if(arg){
        backend.video_on()
    }
    else {
        backend.video_off()
    }
});

ipcMain.on("online_list_request", (event, arg)=>{
    var res = backend.client.get("online_list", (err,val)=> {
        let online_list = JSON.parse(val.toString(2));
        event.sender.send("online_list",online_list);
    });
    
    //console.log(online_list);
    
});




console.log("Hello after the app got ready")









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




