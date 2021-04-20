const electron = require('electron');
const url = require('url');
const path = require('path');


const{app, BrowserWindow, Menu} = electron;
let mainwindow;
let addWindow;

// Listen for the app to be ready
app.on('ready', function(){
    // Create new window
    mainwindow = new BrowserWindow({});
    // Load the first HTML file in the window
    mainwindow.loadURL(url.format({
        pathname: path.join(__dirname, 'screen1.html'),
        protocol:'file:', 
        slashes: true
}));


    // Quit app when closed
    mainwindow.on('closed', function(){
        app.quit();
    })

    // Build menu from template
    const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
    // Insert Menu
    Menu.setApplicationMenu(mainMenu);
});

// Handle create add window
function createAddWindow(){
     // Create new window
     addWindow = new BrowserWindow({
         width: 200,
         height: 200,
         title: 'Calling'

     });
     // Load the second HTML file in the window
     addWindow.loadURL(url.format({
         pathname: path.join(__dirname, 'screen2.html'),
         protocol:'file:', 
         slashes: true
 }));

}


// Create menu template
const mainMenuTemplate = [
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
