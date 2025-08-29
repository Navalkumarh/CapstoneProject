import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
  constructor(private auth: AuthService){}
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const isApi = req.url.startsWith(`${environment.gatewayUrl}/api`);
    if (isApi && this.auth.token){
      req = req.clone({ setHeaders: { Authorization: `Bearer ${this.auth.token}` } });
    }
    return next.handle(req);
  }
}
