import { EventEmitter } from 'events';

interface BackendStatus {
    message: string;
    is_visible: boolean;
}

interface TaskUpdate {
    message: string;
}

interface BackendServiceEvents {
    connected: () => void;
    disconnected: () => void;
    error: (error: Event) => void;
    status: (data: BackendStatus) => void;
    task_update: (data: TaskUpdate) => void;
}

class BackendService extends EventEmitter {
    private eventSource: EventSource | null = null;
    private static instance: BackendService;
    private isConnected: boolean = false;

    private constructor() {
        super();
    }

    public static getInstance(): BackendService {
        if (!BackendService.instance) {
            BackendService.instance = new BackendService();
        }
        return BackendService.instance;
    }

    public connect(): void {
        if (this.isConnected) return;

        this.eventSource = new EventSource('http://localhost:5000/events');
        
        this.eventSource.onopen = () => {
            this.isConnected = true;
            this.emit('connected');
        };

        this.eventSource.onerror = (error) => {
            console.error('SSE Error:', error);
            this.isConnected = false;
            this.emit('error', error);
        };

        this.eventSource.addEventListener('status', (event) => {
            const data = JSON.parse(event.data) as BackendStatus;
            this.emit('status', data);
        });

        this.eventSource.addEventListener('task_update', (event) => {
            const data = JSON.parse(event.data) as TaskUpdate;
            this.emit('task_update', data);
        });
    }

    public disconnect(): void {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            this.isConnected = false;
            this.emit('disconnected');
        }
    }

    public async stopBackend(): Promise<void> {
        try {
            await fetch('http://localhost:5000/stop');
        } catch (error) {
            console.error('Error stopping backend:', error);
        }
    }

    // Type-safe event emitter methods
    public on<K extends keyof BackendServiceEvents>(event: K, listener: BackendServiceEvents[K]): this {
        return super.on(event, listener);
    }

    public emit<K extends keyof BackendServiceEvents>(event: K, ...args: Parameters<BackendServiceEvents[K]>): boolean {
        return super.emit(event, ...args);
    }
}

export default BackendService; 