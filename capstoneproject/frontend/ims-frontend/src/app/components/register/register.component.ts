import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({ selector:'app-register', templateUrl:'./register.component.html' })
export class RegisterComponent {
  username=''; password=''; confirm=''; user_id: any = '';
  constructor(private auth: AuthService, private router: Router){}
  doRegister(){
    if (this.password !== this.confirm){ alert('Passwords do not match'); return; }
    const uid = Number(this.user_id);
    if (isNaN(uid) || uid < 0){ alert('User ID must be a non-negative number'); return; }
    this.auth.register(this.username, this.password, uid).subscribe({
      next: () => { alert('Registered. Please login.'); this.router.navigateByUrl('/login'); },
      error: (err)=> alert(err?.error?.error || 'Registration failed')
    });
  }
}
