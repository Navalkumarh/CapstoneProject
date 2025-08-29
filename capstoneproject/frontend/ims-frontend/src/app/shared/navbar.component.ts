import { Component } from '@angular/core';
import { AuthService } from '../services/auth.service';
@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styles: [`.header-grad{background:linear-gradient(90deg,#0d6efd,#5a8bf2)} .navbar-brand img{border-radius:6px}`]
})
export class NavbarComponent {
  constructor(public auth: AuthService){}
  logout(){ this.auth.logout(); }
}
