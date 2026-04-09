import csv
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


GRIEVANCE_FILE = "grievances.csv"
LOG_FILE = "grievance_logs.csv"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
CATEGORIES = [
    "Academic",
    "Examination",
    "Hostel",
    "Transport",
    "Administration",
    "Others",
]
STATUSES = ["Submitted", "Under Review", "In Process", "Resolved", "Rejected"]
ADMIN_PASSWORD = "admin123"  # Change this for your project demo


class Grievance:
    def __init__(
        self,
        grievance_id: str,
        student_name: str,
        reg_no: str,
        category: str,
        description: str,
        submission_date: str,
        assigned_authority: str = "Not Assigned",
        status: str = "Submitted",
        remarks: str = "",
        priority: str = "Medium",
        resolution_date: str = "",
        document_path: str = "",
    ):
        self.grievance_id = grievance_id
        self.student_name = student_name
        self.reg_no = reg_no
        self.category = category
        self.description = description
        self.submission_date = submission_date
        self.assigned_authority = assigned_authority
        self.status = status
        self.remarks = remarks
        self.priority = priority
        self.resolution_date = resolution_date
        self.document_path = document_path

    def to_dict(self) -> Dict[str, str]:
        return {
            "grievance_id": self.grievance_id,
            "student_name": self.student_name,
            "reg_no": self.reg_no,
            "category": self.category,
            "description": self.description,
            "submission_date": self.submission_date,
            "assigned_authority": self.assigned_authority,
            "status": self.status,
            "remarks": self.remarks,
            "priority": self.priority,
            "resolution_date": self.resolution_date,
            "document_path": self.document_path,
        }

    @staticmethod
    def from_dict(row: Dict[str, str]) -> "Grievance":
        return Grievance(
            grievance_id=row.get("grievance_id", ""),
            student_name=row.get("student_name", ""),
            reg_no=row.get("reg_no", ""),
            category=row.get("category", "Others"),
            description=row.get("description", ""),
            submission_date=row.get("submission_date", ""),
            assigned_authority=row.get("assigned_authority", "Not Assigned"),
            status=row.get("status", "Submitted"),
            remarks=row.get("remarks", ""),
            priority=row.get("priority", "Medium"),
            resolution_date=row.get("resolution_date", ""),
            document_path=row.get("document_path", ""),
        )


class GrievanceManager:
    grievance_headers = [
        "grievance_id",
        "student_name",
        "reg_no",
        "category",
        "description",
        "submission_date",
        "assigned_authority",
        "status",
        "remarks",
        "priority",
        "resolution_date",
        "document_path",
    ]
    log_headers = ["grievance_id", "action", "date", "performed_by"]

    def __init__(self, grievance_file: str = GRIEVANCE_FILE, log_file: str = LOG_FILE):
        self.grievance_file = grievance_file
        self.log_file = log_file
        self._ensure_files()

    def _ensure_files(self) -> None:
        if not os.path.exists(self.grievance_file):
            with open(self.grievance_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.grievance_headers)
                writer.writeheader()
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.log_headers)
                writer.writeheader()

    def _generate_id(self) -> str:
        return "GRV-" + uuid.uuid4().hex[:8].upper()

    def _current_time(self) -> str:
        return datetime.now().strftime(DATE_FORMAT)

    def _read_all(self) -> List[Grievance]:
        grievances: List[Grievance] = []
        with open(self.grievance_file, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                grievances.append(Grievance.from_dict(row))
        return grievances

    def _write_all(self, grievances: List[Grievance]) -> None:
        with open(self.grievance_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.grievance_headers)
            writer.writeheader()
            for grievance in grievances:
                writer.writerow(grievance.to_dict())

    def _add_log(self, grievance_id: str, action: str, performed_by: str) -> None:
        with open(self.log_file, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.log_headers)
            writer.writerow(
                {
                    "grievance_id": grievance_id,
                    "action": action,
                    "date": self._current_time(),
                    "performed_by": performed_by,
                }
            )

    def submit_grievance(
        self,
        student_name: str,
        reg_no: str,
        category: str,
        description: str,
        priority: str = "Medium",
        document_path: str = "",
    ) -> str:
        grievance_id = self._generate_id()
        grievance = Grievance(
            grievance_id=grievance_id,
            student_name=student_name.strip(),
            reg_no=reg_no.strip(),
            category=category.strip() if category in CATEGORIES else "Others",
            description=description.strip(),
            submission_date=self._current_time(),
            priority=priority.strip().title() if priority else "Medium",
            document_path=document_path.strip(),
        )
        with open(self.grievance_file, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.grievance_headers)
            writer.writerow(grievance.to_dict())
        self._add_log(grievance_id, "Grievance submitted", reg_no)
        return grievance_id

    def list_all_grievances(self) -> List[Grievance]:
        return self._read_all()

    def find_by_id(self, grievance_id: str) -> Optional[Grievance]:
        grievance_id = grievance_id.strip().upper()
        for grievance in self._read_all():
            if grievance.grievance_id.upper() == grievance_id:
                return grievance
        return None

    def find_by_reg_no(self, reg_no: str) -> List[Grievance]:
        reg_no = reg_no.strip()
        return [g for g in self._read_all() if g.reg_no == reg_no]

    def update_grievance(
        self,
        grievance_id: str,
        new_status: Optional[str] = None,
        assigned_authority: Optional[str] = None,
        remarks: Optional[str] = None,
        performed_by: str = "Admin",
    ) -> bool:
        grievances = self._read_all()
        updated = False
        grievance_id = grievance_id.strip().upper()

        for grievance in grievances:
            if grievance.grievance_id.upper() == grievance_id:
                if new_status:
                    if new_status not in STATUSES:
                        raise ValueError("Invalid status selected.")
                    grievance.status = new_status
                    if new_status in ("Resolved", "Rejected"):
                        grievance.resolution_date = self._current_time()
                if assigned_authority is not None and assigned_authority.strip():
                    grievance.assigned_authority = assigned_authority.strip()
                if remarks is not None:
                    grievance.remarks = remarks.strip()
                updated = True
                break

        if updated:
            self._write_all(grievances)
            status_text = new_status if new_status else "Details updated"
            self._add_log(grievance_id, f"Updated: {status_text}", performed_by)
        return updated

    def get_logs(self, grievance_id: str) -> List[Dict[str, str]]:
        logs: List[Dict[str, str]] = []
        grievance_id = grievance_id.strip().upper()
        with open(self.log_file, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("grievance_id", "").upper() == grievance_id:
                    logs.append(row)
        return logs

    def pending_count(self) -> int:
        return sum(1 for g in self._read_all() if g.status not in ("Resolved", "Rejected"))


class Analytics:
    def __init__(self, grievance_file: str = GRIEVANCE_FILE):
        self.grievance_file = grievance_file

    def _load_dataframe(self):
        if pd is None:
            raise ImportError("Pandas is not installed. Install it using: pip install pandas")
        df = pd.read_csv(self.grievance_file)
        if df.empty:
            return df
        df["submission_date"] = pd.to_datetime(df["submission_date"], errors="coerce")
        df["resolution_date"] = pd.to_datetime(df["resolution_date"], errors="coerce")
        return df

    def show_summary(self) -> None:
        df = self._load_dataframe()
        if df.empty:
            print("No grievance data available for analysis.")
            return

        print("\n===== ANALYTICS SUMMARY =====")
        print("Total grievances:", len(df))
        print("Pending grievances:", int((~df["status"].isin(["Resolved", "Rejected"])).sum()))
        print("Resolved grievances:", int((df["status"] == "Resolved").sum()))
        print("Rejected grievances:", int((df["status"] == "Rejected").sum()))

        print("\nCategory-wise grievance count:")
        print(df["category"].value_counts().to_string())

        if np is not None:
            resolved_df = df.dropna(subset=["submission_date", "resolution_date"]).copy()
            if not resolved_df.empty:
                resolution_days = (
                    resolved_df["resolution_date"] - resolved_df["submission_date"]
                ).dt.total_seconds() / (24 * 3600)
                print(f"\nAverage resolution time: {np.mean(resolution_days):.2f} days")
            else:
                print("\nAverage resolution time: Not enough resolved data")
        else:
            print("\nInstall NumPy to compute average resolution time.")

        df["month"] = df["submission_date"].dt.to_period("M").astype(str)
        print("\nMonthly grievance trends:")
        print(df["month"].value_counts().sort_index().to_string())

    def generate_charts(self) -> None:
        if plt is None:
            raise ImportError("Matplotlib is not installed. Install it using: pip install matplotlib")
        df = self._load_dataframe()
        if df.empty:
            print("No grievance data available to generate charts.")
            return

        # Bar chart: category count
        category_counts = df["category"].value_counts()
        plt.figure(figsize=(8, 5))
        category_counts.plot(kind="bar")
        plt.title("Number of Grievances per Category")
        plt.xlabel("Category")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig("category_chart.png")
        plt.close()

        # Pie chart: status distribution
        status_counts = df["status"].value_counts()
        plt.figure(figsize=(7, 7))
        status_counts.plot(kind="pie", autopct="%1.1f%%")
        plt.title("Grievance Status Distribution")
        plt.ylabel("")
        plt.tight_layout()
        plt.savefig("status_pie_chart.png")
        plt.close()

        # Line chart: monthly trends
        df["month"] = df["submission_date"].dt.to_period("M").astype(str)
        monthly_counts = df.groupby("month").size()
        plt.figure(figsize=(8, 5))
        monthly_counts.plot(kind="line", marker="o")
        plt.title("Monthly Grievance Submission Trends")
        plt.xlabel("Month")
        plt.ylabel("Number of Grievances")
        plt.tight_layout()
        plt.savefig("monthly_trend_chart.png")
        plt.close()

        print("Charts generated successfully:")
        print("- category_chart.png")
        print("- status_pie_chart.png")
        print("- monthly_trend_chart.png")


def print_categories() -> None:
    print("\nAvailable Categories:")
    for index, category in enumerate(CATEGORIES, start=1):
        print(f"{index}. {category}")


def print_statuses() -> None:
    print("\nAvailable Statuses:")
    for index, status in enumerate(STATUSES, start=1):
        print(f"{index}. {status}")


def submit_flow(manager: GrievanceManager) -> None:
    print("\n===== SUBMIT GRIEVANCE =====")
    student_name = input("Enter student name: ").strip()
    reg_no = input("Enter registration number: ").strip()
    print_categories()
    try:
        category_index = int(input("Choose category number: ")) - 1
        category = CATEGORIES[category_index]
    except (ValueError, IndexError):
        category = "Others"
        print("Invalid category. 'Others' selected.")
    description = input("Enter grievance description: ").strip()
    priority = input("Enter priority (Low/Medium/High): ").strip().title() or "Medium"
    document_path = input("Enter supporting document path (optional): ").strip()

    if not student_name or not reg_no or not description:
        print("Student name, registration number, and description are required.")
        return

    grievance_id = manager.submit_grievance(
        student_name=student_name,
        reg_no=reg_no,
        category=category,
        description=description,
        priority=priority,
        document_path=document_path,
    )
    print(f"Grievance submitted successfully. Your Grievance ID is: {grievance_id}")


def student_tracking_flow(manager: GrievanceManager) -> None:
    print("\n===== TRACK MY GRIEVANCES =====")
    reg_no = input("Enter your registration number: ").strip()
    grievances = manager.find_by_reg_no(reg_no)
    if not grievances:
        print("No grievances found for this registration number.")
        return

    for grievance in grievances:
        print("\n-------------------------------")
        print("Grievance ID      :", grievance.grievance_id)
        print("Category          :", grievance.category)
        print("Description       :", grievance.description)
        print("Submission Date   :", grievance.submission_date)
        print("Assigned Authority:", grievance.assigned_authority)
        print("Status            :", grievance.status)
        print("Priority          :", grievance.priority)
        print("Remarks           :", grievance.remarks or "No remarks")
        print("Resolution Date   :", grievance.resolution_date or "Not resolved yet")


def admin_menu(manager: GrievanceManager) -> None:
    password = input("Enter admin password: ").strip()
    if password != ADMIN_PASSWORD:
        print("Incorrect password.")
        return

    analytics = Analytics(manager.grievance_file)

    while True:
        print("\n===== ADMIN DASHBOARD =====")
        print("1. View all grievances")
        print("2. Search grievance by ID")
        print("3. Update grievance status")
        print("4. View grievance logs")
        print("5. Show analytics summary")
        print("6. Generate charts")
        print("7. Back to main menu")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            grievances = manager.list_all_grievances()
            if not grievances:
                print("No grievances found.")
                continue
            for grievance in grievances:
                print("\n-------------------------------")
                print("Grievance ID      :", grievance.grievance_id)
                print("Student Name      :", grievance.student_name)
                print("Registration No   :", grievance.reg_no)
                print("Category          :", grievance.category)
                print("Status            :", grievance.status)
                print("Priority          :", grievance.priority)
                print("Assigned Authority:", grievance.assigned_authority)
                print("Submission Date   :", grievance.submission_date)
                print("Remarks           :", grievance.remarks or "No remarks")
        elif choice == "2":
            grievance_id = input("Enter grievance ID: ").strip()
            grievance = manager.find_by_id(grievance_id)
            if grievance is None:
                print("Grievance not found.")
            else:
                print("\nGrievance ID      :", grievance.grievance_id)
                print("Student Name      :", grievance.student_name)
                print("Registration No   :", grievance.reg_no)
                print("Category          :", grievance.category)
                print("Description       :", grievance.description)
                print("Submission Date   :", grievance.submission_date)
                print("Assigned Authority:", grievance.assigned_authority)
                print("Status            :", grievance.status)
                print("Priority          :", grievance.priority)
                print("Remarks           :", grievance.remarks or "No remarks")
                print("Resolution Date   :", grievance.resolution_date or "Not resolved yet")
        elif choice == "3":
            grievance_id = input("Enter grievance ID: ").strip()
            print_statuses()
            try:
                status_index = int(input("Choose new status number: ")) - 1
                new_status = STATUSES[status_index]
            except (ValueError, IndexError):
                print("Invalid status selected.")
                continue
            assigned_authority = input("Enter assigned authority/committee: ").strip()
            remarks = input("Enter remarks: ").strip()
            try:
                updated = manager.update_grievance(
                    grievance_id=grievance_id,
                    new_status=new_status,
                    assigned_authority=assigned_authority,
                    remarks=remarks,
                    performed_by="Admin",
                )
                print("Grievance updated successfully." if updated else "Grievance not found.")
            except ValueError as error:
                print(error)
        elif choice == "4":
            grievance_id = input("Enter grievance ID: ").strip()
            logs = manager.get_logs(grievance_id)
            if not logs:
                print("No logs found for this grievance ID.")
            else:
                for log in logs:
                    print(f"{log['date']} | {log['performed_by']} | {log['action']}")
        elif choice == "5":
            try:
                analytics.show_summary()
            except ImportError as error:
                print(error)
        elif choice == "6":
            try:
                analytics.generate_charts()
            except ImportError as error:
                print(error)
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please try again.")


def main() -> None:
    manager = GrievanceManager()
    while True:
        print("\n===== STUDENT GRIEVANCE REDRESSAL SYSTEM =====")
        print("1. Submit grievance")
        print("2. Track my grievances")
        print("3. Admin dashboard")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            submit_flow(manager)
        elif choice == "2":
            student_tracking_flow(manager)
        elif choice == "3":
            admin_menu(manager)
        elif choice == "4":
            print("Thank you for using SGRS.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
