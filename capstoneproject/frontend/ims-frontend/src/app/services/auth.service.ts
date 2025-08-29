import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { environment } from "../../environments/environment";
import { Router } from "@angular/router";

@Injectable({ providedIn: "root" })
export class AuthService {
  private base = `${environment.gatewayUrl}/api/auth`;
  token: string | null = sessionStorage.getItem("token");
  role: string | null = sessionStorage.getItem("role");
  userId: number = Number(sessionStorage.getItem("user_id") || 0);

  constructor(private http: HttpClient, private router: Router) {}

  get isLoggedIn() {
    return !!this.token;
  }

  isAdmin(): boolean {
    return this.role === "admin";
  }

  login(username: string, password: string) {
    return this.http.post<any>(`${this.base}/login`, { username, password });
  }
  register(username: string, password: string, user_id: number) {
    return this.http.post<any>(`${this.base}/register`, {
      username,
      password,
      user_id,
    });
  }

  setSession(data: any) {
    this.token = data.token;
    this.role = data.role;
    this.userId = data.user_id;
    sessionStorage.setItem("token", this.token || "");
    sessionStorage.setItem("role", this.role || "");
    sessionStorage.setItem("user_id", String(this.userId || 0));
  }
  logout() {
    this.token = null;
    this.role = null;
    this.userId = 0;
    sessionStorage.clear();
    this.router.navigateByUrl("/");
  }
}
