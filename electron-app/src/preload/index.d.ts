import type { ElectronAPI } from "@electron-toolkit/preload"

declare global {
  interface Window {
    electron: ElectronAPI & {
      ipcRenderer: {
        send(channel: string, ...args: any[]): void
      }
    }
    api: unknown
  }
}

