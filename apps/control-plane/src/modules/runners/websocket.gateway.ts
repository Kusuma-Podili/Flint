import { WebSocket } from 'ws';

export class RunnerWebSocketGateway {
  private clients: Map<string, WebSocket> = new Map();

  public handleConnection(runnerId: string, socket: WebSocket): void {
    this.clients.set(runnerId, socket);
    console.log(`[WS-GATEWAY] Runner connected: ${runnerId}`);
  }

  public streamLogChunk(runId: string, chunk: any): void {
    const message = JSON.stringify({ event: 'LOG_CHUNK', runId, data: chunk });
    for (const socket of this.clients.values()) {
      socket.send(message);
    }
  }
}
