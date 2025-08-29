import { Component, OnInit } from "@angular/core";
import { PolicyService } from "../../services/policy.service";
import { ClaimService } from "../../services/claim.service";
import { AuthService } from "../../services/auth.service";

@Component({
  selector: "app-user-dashboard",
  templateUrl: "./user-dashboard.component.html",
})
export class UserDashboardComponent implements OnInit {
  policies: any[] = [];
  claims: any[] = [];
  userId = 0;
  newClaim: any = { policy_number: "", description: "" };
  file: File | null = null;
  constructor(
    private policySvc: PolicyService,
    private claimSvc: ClaimService,
    private auth: AuthService
  ) {}
  ngOnInit() {
    this.userId = this.auth.userId;
    this.load();
  }
  load() {
    this.policySvc
      .byUser(this.userId)
      .subscribe((p: any) => (this.policies = p || []));
    this.claimSvc
      .byUser(this.userId)
      .subscribe((c: any) => (this.claims = c || []));
  }

  getPendingClaims(): number {
    return this.claims.filter((claim) => claim.status === "Pending").length;
  }
  onFile(e: any) {
    this.file = e.target.files && e.target.files[0] ? e.target.files[0] : null;
  }
  submit() {
    const fd = new FormData();
    fd.append("policy_number", this.newClaim.policy_number);
    fd.append("description", this.newClaim.description);
    if (this.file) fd.append("file", this.file);
    this.claimSvc.createForm(fd).subscribe({
      next: () => {
        this.newClaim = { policy_number: "", description: "" };
        this.file = null;
        this.load();
      },
      error: (err) => alert(err?.error?.error || "Failed to submit claim"),
    });
  }
  attachmentUrl(c: any, dl: boolean = false) {
    return this.claimSvc.attachmentUrl(c.attachment, dl);
  }
  remove(id: number) {
    if (!confirm("Delete claim?")) return;
    this.claimSvc.remove(id).subscribe(() => this.load());
  }
}
