import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = `${environment.gatewayUrl}/api`;
  constructor(private http: HttpClient) {}
  get(path: string){ return this.http.get(this.base + path); }
  post(path: string, body: any){ return this.http.post(this.base + path, body); }
  put(path: string, body: any){ return this.http.put(this.base + path, body); }
  delete(path: string){ return this.http.delete(this.base + path); }
}
