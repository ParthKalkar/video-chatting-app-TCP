const electron = require('electron');
const url = require('url');
const path = require('path');


const{app, BrowserWindow, ipcMain} = electron;
let mainwindow;
let addWindow;

// Listen for the app to be ready
app.on('ready', function(){
    // Create new window
    mainwindow = new BrowserWindow({});
    mainwindow.maximize()
    mainwindow.removeMenu()
    // Load the first HTML file in the window
    mainwindow.loadURL(url.format({
        pathname: path.join(__dirname, 'home.html'),
        protocol:'file:', 
        slashes: true
}));


    // Quit app when closed
    mainwindow.on('closed', function(){
        app.quit();
    })

    // Build menu from template
    //const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
    // Insert Menu
    //Menu.setApplicationMenu(mainMenu);
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
    element.src = element.bln ? "./Images/mic-on.svg" : "./Images/mic-off.svg";
    element.bln = !element.bln;  /* assigns opposite boolean value always */
}

// Create menu template
/*const mainMenuTemplate = [
    {
        label: 'Call',
        submenu:[
            {
                label: 'Voice Call',
                click(){
                    createAddWindow();
                }
            },
            {
                label: 'Video Call'
            }

        ]
    },
    {
        label: 'Message',
        submenu:[
            {
                label: 'Text Message'
            },
            {
                label: 'Voice Message'
            }
        ]
    },
    {
        label: 'Setting',
    },
    {
        label: 'Quit',
        accelerator: process.platform == 'darwin' ? 'Command+Q' : 
        'Ctrl+Q', 
        click(){
            app.quit();
        }
    }
]

// If mac, add empty object to menu
if(process.platform == 'darwin'){
    mainMenuTemplate.unshift({});
}

// Add Developer tools item if not in production
if(process.env.NODE_ENV !=='production'){
    mainMenuTemplate.push({
        label: 'Developer Tools',
        
        submenu:[
            {
            label: 'Toggle DevTools',
            accelerator: process.platform == 'darwin' ? 'Command+I' : 
            'Ctrl+I', 
            click(item, focusedWindow){
                focusedWindow.toggleDevTools();

            }
        },
        {
            role: 'reload'
        }
    ]
    })
}*/