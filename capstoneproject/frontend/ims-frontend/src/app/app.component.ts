import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `<app-navbar></app-navbar><div class="container my-3"><router-outlet></router-outlet></div>`
})
export class AppComponent {}
