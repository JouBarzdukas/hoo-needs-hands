import { app, shell, BrowserWindow, ipcMain, screen, Tray, Menu, nativeImage } from "electron"
import { join } from "path"
import { electronApp, optimizer, is } from "@electron-toolkit/utils"

let tray: Tray;

function createWindow(): void {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize

  const windowWidth = 320
  const windowHeight = 180 // Default height (non-expanded)

  const x = screenWidth - windowWidth - 5 // 5px margin from right
  const y = 35 // 35px from the top

  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x: x,
    y: y,
    frame: false,
    alwaysOnTop: true,
    resizable: true,
    show: false,
    autoHideMenuBar: true,
    transparent: true,
    backgroundColor: "#00000000", // Fully transparent background
    hasShadow: false,
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      sandbox: false,
    },
  })

  // Make the window ignore mouse events in transparent areas
  // This will allow clicking through the transparent parts of the app
  mainWindow.setIgnoreMouseEvents(false)

  mainWindow.on("ready-to-show", () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: "deny" }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    mainWindow.loadURL(process.env["ELECTRON_RENDERER_URL"])
  } else {
    mainWindow.loadFile(join(__dirname, "../renderer/index.html"))
  }

  // Listen for window resize events from renderer
  ipcMain.on("resize-window", (_, height) => {
    const [width] = mainWindow.getSize()
    mainWindow.setSize(width, height)
  })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId("com.electron")

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on("browser-window-created", (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  
  // IPC test
  ipcMain.on("ping", () => console.log("pong"))

  createWindow()

  app.on("activate", () => {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })

  if (process.platform === "darwin" && app.dock) {
    // const image = nativeImage.createFromPath('/Users/pradeepravi/Documents/hoo-needs-hands/electron-app/resources/icon2.png');
    // const image = nativeImage.createFromPath(join(__dirname, 'icon2.png'))
    const image = nativeImage.createFromPath('/Users/pradeepravi/Documents/hoo-needs-hands/electron-app/resources/icon2.png')
    app.dock.setIcon(image);
  }
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit()
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.

