import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class ClaimService {
  constructor(private api: ApiService, private auth: AuthService) {}
  list(){ return this.api.get('/claims'); }
  get(id:number){ return this.api.get(`/claims/${id}`); }
  create(payload:any){ return this.api.post('/claims', payload); }
  createForm(form: FormData){ return this.api.post('/claims', form); }
  update(id:number,payload:any){ return this.api.put(`/claims/${id}`, payload); }
  remove(id:number){ return this.api.delete(`/claims/${id}`); }
  approve(id:number, remarks:string){ return this.api.post(`/claims/${id}/approve`, {remarks}); }
  reject(id:number, remarks:string){ return this.api.post(`/claims/${id}/reject`, {remarks}); }
  byUser(userId:number){ return this.api.get(`/claims/by-user/${userId}`); }
  attachmentUrl(filename:string, dl:boolean=false){
    const token = this.auth.token;
    const q = `?token=${token}${dl ? '&dl=1' : ''}`;
    return `${environment.gatewayUrl}/uploads/${encodeURIComponent(filename)}${q}`;
  }
}
