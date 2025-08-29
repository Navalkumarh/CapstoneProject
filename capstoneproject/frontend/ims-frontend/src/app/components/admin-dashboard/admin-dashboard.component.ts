import { Component, OnInit } from "@angular/core";
import { PolicyService } from "../../services/policy.service";
import { ClaimService } from "../../services/claim.service";

@Component({
  selector: "app-admin-dashboard",
  templateUrl: "./admin-dashboard.component.html",
})
export class AdminDashboardComponent implements OnInit {
  policies: any[] = [];
  claims: any[] = [];
  policyQuery = "";
  suggestions: any[] = [];
  showCreate = false;
  activeTab = "policies";

  newPolicy: any = {
    policy_number: "",
    customer_name: "",
    type: "",
    premium: 0,
    start_date: "",
    end_date: "",
    user_id: 0,
  };
  editPolicy: any = null;

  remarksMap: Record<number, string> = {};
  claimUserIdMap: Record<number, number> = {};

  constructor(
    private policySvc: PolicyService,
    private claimSvc: ClaimService
  ) {}
  ngOnInit() {
    this.loadAll();
  }

  attachment(c: any, dl: boolean = false) {
    return this.claimSvc.attachmentUrl(c.attachment, dl);
  }

  loadAll() {
    this.policySvc.list().subscribe((d: any) => (this.policies = d || []));
    this.refreshClaims();
  }

  refreshClaimsForUser(uid: number) {
    this.claimSvc.byUser(uid).subscribe((cs: any) => {
      this.claims = cs || [];
      this.decorateClaims();
    });
  }

  refreshClaims() {
    this.claimSvc.list().subscribe((cs: any) => {
      this.claims = cs || [];
      this.decorateClaims();
    });
  }

  private decorateClaims() {
    this.claimUserIdMap = {};
    this.remarksMap = {};
    this.claims.forEach((c) => {
      this.remarksMap[c.claim_id] = c.remarks || "";
      this.policySvc.verify(c.policy_number).subscribe((res: any) => {
        const p = res?.policy;
        if (p) {
          this.claimUserIdMap[c.claim_id] = p.user_id;
        }
      });
    });
  }

  search() {
    const q = this.policyQuery.trim();
    if (!q) {
      this.loadAll();
      return;
    }
    const asNum = Number(q);
    const isUserId = !isNaN(asNum) && q.match(/^\d+$/);
    if (isUserId) {
      this.policySvc
        .byUser(asNum)
        .subscribe((p: any) => (this.policies = p || []));
      this.refreshClaimsForUser(asNum);
    } else {
      this.policySvc.search(q).subscribe((d: any) => (this.policies = d || []));
      this.refreshClaims();
    }
  }

  reset() {
    this.policyQuery = "";
    this.suggestions = [];
    this.loadAll();
  }

  onQueryChange() {
    const q = this.policyQuery.trim();
    if (!q || q.match(/^\d+$/)) {
      this.suggestions = [];
      return;
    }
    this.policySvc
      .search(q)
      .subscribe((res: any) => (this.suggestions = res || []));
  }
  useSuggestion(s: any) {
    this.policyQuery = s.policy_number;
    this.search();
    this.suggestions = [];
  }

  toggleCreate() {
    this.showCreate = !this.showCreate;
  }
  create() {
    if (this.newPolicy.premium < 0 || this.newPolicy.user_id < 0) {
      alert("Premium and User ID must be non-negative.");
      return;
    }
    if (
      !this.newPolicy.start_date ||
      !this.newPolicy.end_date ||
      new Date(this.newPolicy.end_date) <= new Date(this.newPolicy.start_date)
    ) {
      alert("End date must be greater than start date");
      return;
    }
    this.policySvc.create(this.newPolicy).subscribe(() => {
      this.newPolicy = {
        policy_number: "",
        customer_name: "",
        type: "",
        premium: 0,
        start_date: "",
        end_date: "",
        user_id: 0,
      };
      this.loadAll();
      this.showCreate = false;
    });
  }
  startEdit(p: any) {
    this.editPolicy = { ...p };
    this.showCreate = false;
  }
  update() {
    if (this.editPolicy.premium < 0 || this.editPolicy.user_id < 0) {
      alert("Premium and User ID must be non-negative.");
      return;
    }
    if (
      !this.editPolicy.start_date ||
      !this.editPolicy.end_date ||
      new Date(this.editPolicy.end_date) <= new Date(this.editPolicy.start_date)
    ) {
      alert("End date must be greater than start date");
      return;
    }
    this.policySvc
      .update(this.editPolicy.policy_id, this.editPolicy)
      .subscribe(() => {
        this.editPolicy = null;
        this.loadAll();
      });
  }
  remove(id: number) {
    if (!confirm("Delete policy?")) return;
    this.policySvc.remove(id).subscribe(() => this.loadAll());
  }

  approve(id: number) {
    const remarks = this.remarksMap[id] || "Approved by admin";
    this.claimSvc.approve(id, remarks).subscribe(() => this.refreshClaims());
  }
  reject(id: number) {
    const remarks = this.remarksMap[id] || "Rejected by admin";
    this.claimSvc.reject(id, remarks).subscribe(() => this.refreshClaims());
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  }

  // Tab management
  setActiveTab(tab: string) {
    this.activeTab = tab;
  }

  // Stats methods
  getPendingClaimsCount(): number {
    return this.claims.filter((claim) => claim.status === "Pending").length;
  }

  getUniqueUsersCount(): number {
    const userIds = new Set();
    this.policies.forEach((policy) => userIds.add(policy.user_id));
    this.claims.forEach((claim) => {
      if (this.claimUserIdMap[claim.claim_id]) {
        userIds.add(this.claimUserIdMap[claim.claim_id]);
      }
    });
    return userIds.size;
  }

  
}
