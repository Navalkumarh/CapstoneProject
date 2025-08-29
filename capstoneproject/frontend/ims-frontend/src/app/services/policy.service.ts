import { Injectable } from '@angular/core';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class PolicyService {
  constructor(private api: ApiService) {}
  list(){ return this.api.get('/policies'); }
  get(id:number){ return this.api.get(`/policies/${id}`); }
  create(payload:any){ return this.api.post('/policies', payload); }
  update(id:number,payload:any){ return this.api.put(`/policies/${id}`, payload); }
  remove(id:number){ return this.api.delete(`/policies/${id}`); }
  search(q:string){ return this.api.get(`/policies/search?q=${encodeURIComponent(q)}`); }
  byUser(userId:number){ return this.api.get(`/policies/by-user/${userId}`); }
  verify(policyNumber:string){ return this.api.get(`/policies/verify/${encodeURIComponent(policyNumber)}`); }
}
