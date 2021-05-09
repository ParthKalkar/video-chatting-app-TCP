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
        backend.client.set("status","initiate_call");
        mainwindow.loadURL(url.format({
            pathname: path.join(__dirname, 'calling.html'),
            protocol:'file:', 
            slashes: true
        }));
    });

    ipcMain.on("call_cancel", (event, arg)=>{
        backend.client.set("calling_status","cancelled");
        mainwindow.loadURL(url.format({
            pathname: path.join(__dirname, 'home.html'),
            protocol:'file:', 
            slashes: true
        }));
        //backend.client.set("status", "home");
    });

    // listen for call
    ipcMain.on("incoming_call_request", (event,arg)=>{
        backend.client.get("status", (err,val)=>{
            if (val == "incoming"){
                mainwindow.loadURL(url.format({
                    pathname: path.join(__dirname, 'receiving-call.html'),
                    protocol:'file:', 
                    slashes: true
                }));
            }
        })
    });

    ipcMain.on("accept_call", (event,call_accepted)=>{
        if(call_accepted){
            backend.client.set("incoming_status", "accepted");
            mainwindow.loadURL(url.format({
                pathname: path.join(__dirname, 'on-call.html'),
                protocol:'file:', 
                slashes: true
            }));
        }
        else{
            backend.client.set("incoming_status", "declined");
            mainwindow.loadURL(url.format({
                pathname: path.join(__dirname, 'home.html'),
                protocol:'file:', 
                slashes: true
            }));
        }
    });

    ipcMain.on("call_accepted_request", (event,data)=>{
        backend.client.get("status", (err,val)=>{
            if(val=="call"){
                mainwindow.loadURL(url.format({
                    pathname: path.join(__dirname, 'on-call.html'),
                    protocol:'file:', 
                    slashes: true
                }));
            }
        })
    });

    ipcMain.on("call_finish", (event,data)=>{
        backend.client.set("call_status","finished");
        backend.client.set("status", 'home'); //not sure of this
        mainwindow.loadURL(url.format({
            pathname: path.join(__dirname, 'home.html'),
            protocol:'file:', 
            slashes: true
        }));
    })
    
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

// returns the caller's name
ipcMain.on("correspondent_name_request", (event,arg)=>{
    backend.client.get("correspondent_name", (err,val)=>{
        event.sender.send("correspondent_name", val);
    })
})

ipcMain.on('use_video_request', (event,data)=>{
    backend.client.get('use_video', (err,val)=>{
        event.sender.send('use_video', val=="TRUE");
    })
})

ipcMain.on('use_audio_request', (event,data)=>{
    backend.client.get('use_audio', (err,val)=>{
        event.sender.send('use_audio', val=="TRUE");
    })
})



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




