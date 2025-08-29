import { Component, OnInit } from "@angular/core";
import { AuthService } from "../../services/auth.service";

@Component({
  selector: "app-home",
  templateUrl: "./home.component.html",
})
export class HomeComponent implements OnInit {
  now = new Date();

  constructor(public auth: AuthService) {}

  ngOnInit(): void {}
}
