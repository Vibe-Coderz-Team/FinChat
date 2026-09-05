import os, csv, random
from datetime import datetime, timedelta

def generate_30k_dataset():
    print("Generating 30,000 rows of financial data...")
    
    # 15+ columns per table
    gateway_cols = ['transaction_id', 'merchant_id', 'merchant_name', 'customer_id', 'customer_name', 'customer_email', 'amount', 'currency', 'payment_method', 'card_network', 'card_last4', 'status', 'error_code', 'error_message', 'created_at', 'captured_at']
    bank_cols = ['settlement_id', 'transaction_id', 'bank_name', 'account_last4', 'routing_number', 'swift_code', 'amount', 'currency', 'status', 'failure_reason', 'batch_id', 'settled_at', 'utr_number', 'reference_id', 'metadata']
    ledger_cols = ['entry_id', 'transaction_id', 'account_id', 'type', 'amount', 'currency', 'platform_fee', 'tax', 'net_amount', 'status', 'reconciliation_id', 'notes', 'recorded_at', 'updated_at', 'operator_id']
    
    merchants = [("MER_001", "QuickBites Restaurant"), ("MER_002", "GreenLeaf Pharmacy"), ("MER_003", "ApexRetail"), ("MER_004", "TechCorp Inc"), ("MER_005", "FakeCompany")]
    methods = ["card", "wallet", "upi", "netbanking"]
    banks = ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank"]
    
    gateway_data = []
    bank_data = []
    ledger_data = []
    
    # HARDCODE DEMO TRANSACTIONS SO DEMO WORKS PERFECTLY
    demos = [
        # Exception 13000
        {"id": "TXN_1029", "merch": ("MER_001", "QuickBites Restaurant"), "amt": 13000, "meth": "card", "type": "exception"},
        # Settled Wallet 15000
        {"id": "TXN_1012", "merch": ("MER_002", "GreenLeaf Pharmacy"), "amt": 15000, "meth": "wallet", "type": "settled"},
        # Pending ApexRetail
        {"id": "TXN_5001", "merch": ("MER_003", "ApexRetail"), "amt": 5000, "meth": "upi", "type": "pending"},
    ]
    
    start_time = datetime(2026, 9, 1, 8, 0, 0)
    
    for i in range(1, 30001):
        is_demo = False
        if i <= len(demos):
            d = demos[i-1]
            txn_id = d["id"]
            merch_id, merch_name = d["merch"]
            amt = d["amt"]
            method = d["meth"]
            scenario = d["type"]
            is_demo = True
        else:
            txn_id = f"TXN_{10000+i}"
            merch_id, merch_name = random.choice(merchants)
            amt = round(random.uniform(100, 25000), 2)
            method = random.choice(methods)
            
            rand_val = random.random()
            if rand_val < 0.85: scenario = "settled"
            elif rand_val < 0.90: scenario = "pending"
            elif rand_val < 0.95: scenario = "failed"
            else: scenario = "exception"
            
        created = start_time + timedelta(minutes=i*2)
        captured = created + timedelta(seconds=random.randint(10, 60)) if scenario != "failed" else ""
        
        # Gateway Row
        gateway_data.append({
            'transaction_id': txn_id, 'merchant_id': merch_id, 'merchant_name': merch_name,
            'customer_id': f"CUST_{random.randint(1000,9999)}", 'customer_name': f"Customer {i}", 'customer_email': f"cust{i}@example.com",
            'amount': amt, 'currency': 'INR', 'payment_method': method,
            'card_network': random.choice(['VISA', 'MASTERCARD', 'RUPAY']) if method == 'card' else '',
            'card_last4': f"{random.randint(1000,9999)}" if method == 'card' else '',
            'status': "captured" if scenario in ["settled", "pending", "exception"] else "failed",
            'error_code': "ERR_01" if scenario == "failed" else "", 'error_message': "Insufficient Funds" if scenario == "failed" else "",
            'created_at': created.strftime("%Y-%m-%d %H:%M:%S"), 'captured_at': captured.strftime("%Y-%m-%d %H:%M:%S") if captured else ""
        })
        
        # Bank & Ledger Rows
        if scenario == "settled":
            settled_at = created + timedelta(days=1, hours=random.randint(1, 5))
            bank_data.append({
                'settlement_id': f"STL_{i}", 'transaction_id': txn_id, 'bank_name': random.choice(banks),
                'account_last4': f"{random.randint(1000,9999)}", 'routing_number': "RTG123456", 'swift_code': "SWIFT123",
                'amount': amt, 'currency': 'INR', 'status': "settled", 'failure_reason': "", 'batch_id': f"BATCH_{created.strftime('%Y%m%d')}",
                'settled_at': settled_at.strftime("%Y-%m-%d %H:%M:%S"), 'utr_number': f"UTR{random.randint(10000000,99999999)}",
                'reference_id': f"REF_{i}", 'metadata': "{}"
            })
            ledger_data.append({
                'entry_id': f"LED_{i}", 'transaction_id': txn_id, 'account_id': f"ACC_{merch_id}", 'type': 'credit',
                'amount': amt, 'currency': 'INR', 'platform_fee': round(amt*0.02, 2), 'tax': round(amt*0.003, 2),
                'net_amount': round(amt*0.977, 2), 'status': 'reconciled', 'reconciliation_id': f"REC_{i}",
                'notes': "Auto-reconciled", 'recorded_at': (settled_at + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': "", 'operator_id': "SYS"
            })
        elif scenario == "pending":
            bank_data.append({
                'settlement_id': f"STL_{i}", 'transaction_id': txn_id, 'bank_name': random.choice(banks),
                'account_last4': f"{random.randint(1000,9999)}", 'routing_number': "RTG123456", 'swift_code': "SWIFT123",
                'amount': amt, 'currency': 'INR', 'status': "pending", 'failure_reason': "", 'batch_id': f"BATCH_{created.strftime('%Y%m%d')}",
                'settled_at': "", 'utr_number': "", 'reference_id': f"REF_{i}", 'metadata': "{}"
            })
            ledger_data.append({
                'entry_id': f"LED_{i}", 'transaction_id': txn_id, 'account_id': f"ACC_{merch_id}", 'type': 'credit',
                'amount': amt, 'currency': 'INR', 'platform_fee': round(amt*0.02, 2), 'tax': round(amt*0.003, 2),
                'net_amount': round(amt*0.977, 2), 'status': 'pending', 'reconciliation_id': "",
                'notes': "Awaiting bank settlement", 'recorded_at': created.strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': "", 'operator_id': "SYS"
            })
        # If scenario == "exception", we PURPOSELY don't write bank or ledger rows!
        # If scenario == "failed", gateway status is failed, no bank/ledger rows needed.

    # Write files
    def write_csv(filename, fieldnames, data):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
    write_csv('gateway.csv', gateway_cols, gateway_data)
    write_csv('bank.csv', bank_cols, bank_data)
    write_csv('ledger.csv', ledger_cols, ledger_data)
    
    print("Done! Generated gateway.csv (30000), bank.csv (~27000), ledger.csv (~27000).")

if __name__ == "__main__":
    generate_30k_dataset()
