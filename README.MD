## 🔧 Tech Stack

- **AWS Lambda** – Serverless function to automate cleanup  
- **Amazon EC2 & EBS** – Source of snapshots  
- **Amazon SNS** – Sends email alerts when snapshots are deleted  
- **IAM** – Access control via custom roles and policies  
- **Python (boto3)** – AWS SDK to interact with EC2, Volumes, and SNS

---

## 🚀 Getting Started

### ✅ Step-by-Step Deployment Guide

---

### 1. Launch an EC2 Instance & Snapshot

- Launch a test EC2 instance in any AWS region (e.g., `us-east-1`).
- Attach an EBS volume.
- Go to **EC2 → Volumes → Select volume → Create Snapshot**.

---

### 2. Set Up the Lambda Function

- Go to **AWS Lambda → Create Function**.
- Set **runtime** to **Python 3.12** or later.
- Use the code from `lambda_function.py` in this repository.
- Under **Configuration → General**, set **timeout** to **10 seconds**.
- Deploy the function.

---

### 3. Set Up IAM Permissions

Attach the following permissions to your Lambda's execution role:

- `ec2:DescribeInstances`  
- `ec2:DescribeSnapshots`  
- `ec2:DescribeVolumes`  
- `ec2:DeleteSnapshot`  
- `sns:Publish`  

- create a **custom inline policy** granting exactly the actions above.

---

### 4. Create an SNS Topic for Alerts

- Go to **Amazon SNS → Create Topic → Standard**.
- Name it something like `snapshot-alerts`.
- Add a **subscription method** (e.g., **Email**).
- Confirm the subscription via the email link.

---

### 5. First Test: No Deletion Expected

- Keep the EC2 instance **running**.
- Run the Lambda function from the **Test** tab.
- Expected: No snapshots should be deleted.

---

### 6. Second Test: Trigger Deletion

- **Terminate the EC2 instance**.
- Run Lambda again.
- It will detect stale snapshots and:
  - **Delete** them
  - **Send alert** via SNS to your email
