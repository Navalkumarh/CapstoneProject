import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({ selector:'app-login', templateUrl:'./login.component.html' })
export class LoginComponent {
  username=''; password='';
  constructor(private auth: AuthService, private router: Router){}
  doLogin(){
    this.auth.login(this.username, this.password).subscribe({
      next: (res:any)=>{ this.auth.setSession(res); this.router.navigateByUrl(this.auth.role==='admin' ? '/admin-dashboard' : '/user-dashboard');},
      error: (err)=> alert(err?.error?.error || 'Invalid credentials')
    });
  }
}
