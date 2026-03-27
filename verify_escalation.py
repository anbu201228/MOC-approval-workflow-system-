import time
from datetime import datetime, timedelta, timezone
from app import app, db, MOC, User, ApprovalHistory, check_escalations

def test_escalation():
    print("Starting escalation test...")
    
    # 1. Create MOC
    with app.app_context():
        # Ensure 'employee' user exists
        submitter = User.query.filter_by(username='employee').first()
        if not submitter:
            print("Error: 'employee' user not found.")
            return

        # Clean up old test data
        old_mocs = MOC.query.filter_by(moc_number='TEST-ESC-001').all()
        for m in old_mocs:
            db.session.delete(m)
        db.session.commit()

        # Create MOC
        moc = MOC(
            moc_number='TEST-ESC-001',
            title='Test Escalation MOC',
            date=datetime.now().date(),
            change_category='Test',
            submitted_by=submitter.id,
            status='Submitted',
            current_step=1,
            approver1_id=2, # EHS Manager
            approver2_id=3,
            approver3_id=4,
            approver4_id=5,
            approver1_status='Pending'
        )
        # Backdate updated_at
        four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=4)
        moc.updated_at = four_hours_ago
        
        db.session.add(moc)
        db.session.commit()
        print(f"Created MOC {moc.id}. updated_at={moc.updated_at}")
        
    # 2. Run check_escalations in a FRESH context
    print("Running check_escalations in fresh context...")
    with app.app_context():
        check_escalations()
        
    # 3. Verify in ANOTHER fresh context
    print("Verifying in fresh context...")
    with app.app_context():
        moc = MOC.query.filter_by(moc_number='TEST-ESC-001').first()
        if not moc:
            print("Error: MOC not found.")
            return

        print(f"MOC Status: {moc.status}")
        print(f"Current Step: {moc.current_step}")
        print(f"Approver 1 Status: {moc.approver1_status}")
        print(f"Approver 2 Status: {moc.approver2_status}")

        if moc.approver1_status == 'Timeout' and moc.current_step == 2 and moc.approver2_status == 'Pending':
            print("SUCCESS: MOC escalated to Step 2 due to timeout.")
        else:
            print("FAILURE: Escalation logic did not work as expected.")
            
        # Cleanup
        db.session.delete(moc)
        db.session.commit()
        print("Cleanup done.")

if __name__ == "__main__":
    test_escalation()
