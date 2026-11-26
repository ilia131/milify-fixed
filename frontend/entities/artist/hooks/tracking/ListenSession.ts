import { generateUUID } from "@/shared/lib/generateUUID";

export class ListenSession {
  private sessionId: string;

  constructor() {
    this.sessionId = generateUUID();
  }

  getId(): string {
    return this.sessionId;
  }

  reset(): void {
    this.sessionId = generateUUID();
  }
}