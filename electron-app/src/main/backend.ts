import { spawn } from 'child_process';
import { join } from 'path';

let pythonProcess: any = null;

export function startBackendServer() {
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const serverPath = join(__dirname, '../../backend/server.py');

  pythonProcess = spawn(pythonPath, [serverPath], {
    stdio: 'pipe',
    shell: true
  });

  pythonProcess.stdout.on('data', (data: Buffer) => {
    console.log(`Backend stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data: Buffer) => {
    console.error(`Backend stderr: ${data}`);
  });

  pythonProcess.on('close', (code: number) => {
    console.log(`Backend server exited with code ${code}`);
  });
}

export function stopBackendServer() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
} 