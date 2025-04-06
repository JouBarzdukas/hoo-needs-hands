import { app, shell, BrowserWindow, ipcMain, screen, Tray, Menu, nativeImage } from "electron"
import { join } from "path"
import { electronApp, optimizer, is } from "@electron-toolkit/utils"

let tray: Tray;
let mainWindow: BrowserWindow | null = null

function createTray(): void {
  try {
    const iconPath = process.platform === "win32"
      ? join(__dirname, "../../resources/icon.ico")
      : join(__dirname, "../../resources/icon.png")

    let trayIcon = nativeImage.createFromPath(iconPath)

    if (trayIcon.isEmpty()) {
      console.warn("Tray icon not found or failed to load. Using default Electron icon.")
      trayIcon = nativeImage.createFromNamedImage("electron")
    }

    tray = new Tray(trayIcon.resize({ width: 16, height: 16 }))
    const contextMenu = Menu.buildFromTemplate([
      {
        label: "Show / Hide",
        click: () => {
          if (mainWindow) {
            if (mainWindow.isVisible()) {
              mainWindow.hide()
            } else {
              mainWindow.show()
            }
          }
        },
      },
      { type: "separator" },
      {
        label: "Quit",
        click: () => {
          app.quit()
        },
      },
    ])

    tray.setToolTip("Electron App")
    tray.setContextMenu(contextMenu)

    tray.on("click", () => {
      if (mainWindow) {
        if (mainWindow.isVisible()) {
          mainWindow.hide()
        } else {
          mainWindow.show()
        }
      }
    })
  } catch (err) {
    console.error("Failed to create tray icon:", err)
  }
}

function createWindow(): void {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize

  const windowWidth = 320
  const windowHeight = 180
  const x = screenWidth - windowWidth - 10
  const y = process.platform === "darwin" ? 35 : 10

  const iconPath = process.platform === "win32"
    ? join(__dirname, "../../resources/icon.ico")
    : join(__dirname, "../../resources/icon.png")

  mainWindow = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x,
    y,
    frame: false,
    alwaysOnTop: true,
    resizable: true,
    show: false,
    autoHideMenuBar: true,
    transparent: true,
    backgroundColor: "#00000000",
    hasShadow: false,
    icon: iconPath,
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      sandbox: false,
    },
  })

  mainWindow.setIgnoreMouseEvents(false)

  mainWindow.on("ready-to-show", () => {
    mainWindow?.show()
  })

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: "deny" }
  })

  if (is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    mainWindow.loadURL(process.env["ELECTRON_RENDERER_URL"])
  } else {
    mainWindow.loadFile(join(__dirname, "../renderer/index.html"))
  }

  ipcMain.on("resize-window", (_, height: number) => {
    if (mainWindow) {
      const [width] = mainWindow.getSize()
      mainWindow.setSize(width, height)
    }
  })
}

app.whenReady().then(() => {
  electronApp.setAppUserModelId("com.electron")

  app.on("browser-window-created", (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  ipcMain.on("ping", () => console.log("pong"))

  createWindow()
  createTray()

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on("window-all-closed", () => {
  // Keep app running in tray for all OSes
  // If you'd like to quit on close for non-macOS, uncomment below:
  // if (process.platform !== "darwin") app.quit()
})
