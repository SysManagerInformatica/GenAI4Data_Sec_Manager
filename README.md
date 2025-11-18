# **RLS & CLS Security Manager Setup Guide - v2.0-Nov-2025**

## **1. Introduction**

This guide outlines the steps required to deploy the **RLS & CLS Security Manager** application within your environment.

This enhanced version includes:
- ✅ **Row-Level Security (RLS)** - Control access at the row level
- ✅ **Column-Level Security (CLS)** - Control access at the column level using Policy Tags
- ✅ **Audit Logging** - Track all security operations and changes

**Important Notice:**

**This application is a prototype intended for experimental purposes only. It is not suitable for production use. This software is provided "as is," without any warranties, express or implied, including but not limited to merchantability, fitness for a particular purpose, and non-infringement. Google and the developers shall not be liable for any claims, damages, or other liabilities arising from the use of this software. Use this tool at your own risk. Google is not responsible for its functionality, reliability, or security.**

---

## **2. Prerequisites**

### **2.1 Framework Understanding**

Successful deployment relies on a solid understanding of:

* Your company's business rules and requirements.
* The functional aspects of your workload (e.g., SAP, Salesforce).
* Google Cloud fundamentals and products.
* BigQuery Row-Level Security (RLS) concepts.
* BigQuery Column-Level Security (CLS) and Data Catalog Policy Tags.

### **2.2 Required Knowledge**

Before proceeding, ensure you are familiar with:

* Google Cloud Platform [fundamentals](https://www.coursera.org/lecture/gcp-fundamentals/welcome-to-gcp-fundamentals-I6zpd).
* Navigating the Cloud Console, [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell), and [Cloud Shell Editor](https://cloud.google.com/shell/docs/editor-overview).
* [BigQuery](https://cloud.google.com/bigquery/docs/introduction) fundamentals.
* [Identity and Access Management](https://cloud.google.com/iam/docs/) fundamentals.
* [Data Catalog](https://cloud.google.com/data-catalog/docs) and Policy Tags fundamentals.

---

## **3. Solution Deployment**

### **3.1 Project Setup**

**Note:** When copying commands, ensure no extra blank lines are included, as they can cause errors.

### **3.2 Required Google Cloud Components**

The following Google Cloud components are necessary:

* Google Cloud Project.
* BigQuery instance and datasets.
* Data Catalog (for CLS Policy Tags).
* Cloud Run.
* Service Account.
* Default Artifact Repository.

---

### **3.3 Service Account Configuration**

For running the application on Cloud Run, a dedicated Service Account with the required permissions is recommended.

**Create and Grant Service Account Roles:**

**Important:** Replace the `{value}` placeholders with your specific parameters.

#### **Step 1: Create the Service Account**
```bash
gcloud iam service-accounts create {service_account_name} --display-name="{display_name}"
```

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/CreateServiceAccount.png)

#### **Step 2: Get Service Account Email**
```bash
gcloud iam service-accounts list --project={project_id} --filter="displayName:{service_account_name}" --format="value(email)"
```

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/ListServiceAccount.png)

#### **Step 3: Grant Required Roles**

##### **For RLS (Row-Level Security):**
```bash
gcloud projects add-iam-policy-binding {project_id} --member="serviceAccount:{service_account_email}" --role="roles/bigquery.admin"
gcloud projects add-iam-policy-binding {project_id} --member="serviceAccount:{service_account_email}" --role="roles/run.invoker"
gcloud projects add-iam-policy-binding {project_id} --member="serviceAccount:{service_account_email}" --role="roles/iam.serviceAccountTokenCreator"
```

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/GratingSARoles.png)

##### **For CLS (Column-Level Security) - ADDITIONAL ROLES:**
```bash
gcloud projects add-iam-policy-binding {project_id} --member="serviceAccount:{service_account_email}" --role="roles/datacatalog.admin"
gcloud projects add-iam-policy-binding {project_id} --member="serviceAccount:{service_account_email}" --role="roles/bigquery.dataEditor"
```

![image](https://github.com/SysManagerInformatica/GenAI4Data_Sec_Manager/blob/08420c46bca2f63827ada53a6ea5659405fee7b0/docs/images/GratingCLSRoles.png)
---

### **3.4 BigQuery Dataset and Table Creation**

#### **Step 1: Create the `rls_manager` dataset**
```bash
bq mk --dataset --location={location} {project_id}:rls_manager
```

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/CreateDataset.png)

#### **Step 2: Create RLS Control Tables**

##### **Table 1: `rls_manager.policies`**

This table stores RLS policy definitions.
```sql
CREATE TABLE `{project_id}.rls_manager.policies` (
    policy_type STRING NOT NULL,
    policy_name STRING NOT NULL,
    project_id STRING NOT NULL,
    dataset_id STRING NOT NULL,
    table_name STRING NOT NULL,
    field_id STRING NOT NULL,
    group_email STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    id STRING DEFAULT GENERATE_UUID()
);
```


##### **Table 2: `rls_manager.policies_filters`**

This table stores RLS filter values for policies.
```sql
CREATE TABLE `{project_id}.rls_manager.policies_filters` (
    rls_type STRING NOT NULL,
    policy_name STRING NOT NULL,
    project_id STRING NOT NULL,
    dataset_id STRING NOT NULL,
    table_id STRING NOT NULL,
    field_id STRING NOT NULL,
    filter_value STRING NOT NULL,
    username STRING,
    rls_group STRING,
    service_account STRING,
    domain STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    id STRING DEFAULT GENERATE_UUID()
);
```

##### **Table 3: `rls_manager.audit_logs` - NEW!**

This table stores all audit logs for security operations.
```sql
CREATE TABLE `{project_id}.rls_manager.audit_logs` (
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    user_email STRING,
    action STRING NOT NULL,
    resource_type STRING,
    resource_name STRING,
    status STRING NOT NULL,
    taxonomy STRING,
    error_message STRING,
    details JSON,
    log_id STRING DEFAULT GENERATE_UUID()
);
```

---

### **3.5 Data Catalog Setup (for CLS)**

Column-Level Security requires Data Catalog taxonomies and policy tags.

#### **Step 1: Enable Data Catalog API**
```bash
gcloud services enable datacatalog.googleapis.com --project={project_id}
```
![image](https://github.com/SysManagerInformatica/GenAI4Data_Sec_Manager/blob/717cba956dfcd6f00ac6ccad472698a05b4e4c9f/docs/images/EnableDataCatalog.png)

#### **Step 2: Create a Taxonomy**

You can create taxonomies either via the console or using the application after deployment.


**Example taxonomy structure:**
```
FINANCIAL - Financial Data
  ├── FINANCIAL > teste - Test financial data
  └── FINANCIAL > Teste log financeiro - Financial log test data
```

**Note:** The application includes a full UI for managing taxonomies and policy tags, so you can create them after deployment.

---

### **3.6 Cloning the GitHub Repository**

Use Cloud Shell to clone the GitHub repository:
```bash
cd $HOME
git clone https://github.com/lucascarvalhal/RLS_CLS_Manager_Integrated.git
```

**[IMAGE PLACEHOLDER: Screenshot showing git clone command in Cloud Shell]**

---

### **3.7 Application Configuration**

Navigate to the cloned directory and open the `config.py` file:
```bash
cd $HOME/RLS_CLS_Manager_Integrated
```

Open `config.py` in Cloud Shell Editor and configure the following parameters:
```python
class Config:
    # Project Configuration
    PROJECT_ID = "your-project-id"  # Your GCP Project ID
    LOCATION = "us-central1"        # Location for Data Catalog resources
    
    # BigQuery Configuration
    RLS_DATASET = "rls_manager"     # Dataset for RLS control tables
    
    # Application Configuration
    APP_TITLE = "RLS & CLS Security Manager"
```

**[IMAGE PLACEHOLDER: Screenshot showing config.py file being edited in Cloud Shell Editor]**

**Configuration Parameters:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `PROJECT_ID` | Your Google Cloud Project ID | `my-project-123` |
| `LOCATION` | Location for Data Catalog taxonomies | `us-central1` |
| `RLS_DATASET` | BigQuery dataset for control tables | `rls_manager` |

---

### **3.8 Application Deployment**

**Important:** Replace the `{value}` placeholders with your specific parameters.

Navigate to the application directory and deploy to Cloud Run:
```bash
cd $HOME/RLS_CLS_Manager_Integrated

gcloud run deploy rls-cls-manager \
  --region={region_id} \
  --source . \
  --platform managed \
  --service-account="{service_account_email}" \
  --port=8080 \
  --memory=1Gi \
  --timeout=300 \
  --min-instances=0 \
  --max-instances=3 \
  --allow-unauthenticated \
  --project={project_id}
```

**[IMAGE PLACEHOLDER: Screenshot showing Cloud Run deployment in progress]**

**Deployment Parameters:**

| Parameter | Description | Recommended Value |
|-----------|-------------|-------------------|
| `--memory` | Container memory | `1Gi` |
| `--timeout` | Request timeout | `300` seconds |
| `--min-instances` | Minimum instances | `0` (scale to zero) |
| `--max-instances` | Maximum instances | `3` |

**After deployment, you will receive a Service URL like:**
```
https://rls-cls-manager-[hash]-[region].run.app
```

**[IMAGE PLACEHOLDER: Screenshot showing successful deployment with Service URL]**

---

## **4. Application Features**

### **4.1 Row-Level Security (RLS)**

Manage BigQuery Row-Level Security policies to control data access at the row level.

**Features:**
- ✅ Create RLS policies (User-based and Group-based)
- ✅ Assign users to policies
- ✅ Assign filter values to groups
- ✅ View and manage existing policies

**[IMAGE PLACEHOLDER: Screenshot showing RLS menu in the application]**

---

### **4.2 Column-Level Security (CLS) - NEW!**

Manage BigQuery Column-Level Security using Data Catalog Policy Tags.

#### **4.2.1 Manage Taxonomies**

Create and manage Data Catalog taxonomies.

**Features:**
- ✅ Create new taxonomies
- ✅ View existing taxonomies
- ✅ Delete taxonomies

**[IMAGE PLACEHOLDER: Screenshot showing Taxonomy management page]**

#### **4.2.2 Manage Policy Tags**

Create and organize policy tags within taxonomies.

**Features:**
- ✅ Create new policy tags
- ✅ Create nested/hierarchical tags
- ✅ View tag structure
- ✅ Delete tags

**[IMAGE PLACEHOLDER: Screenshot showing Policy Tags management page]**

#### **4.2.3 Apply Tags to Columns**

Apply policy tags to BigQuery table columns.

**Features:**
- ✅ Browse datasets and tables
- ✅ View column schemas
- ✅ Apply tags to columns
- ✅ Remove tags from columns
- ✅ View tagging statistics

**[IMAGE PLACEHOLDER: Screenshot showing Apply Tags interface with column list]**

---

### **4.3 Audit Logging - NEW!**

Track all security operations and changes.

**Features:**
- ✅ Real-time activity dashboard
- ✅ Filter logs by action, user, status, date
- ✅ View detailed operation information
- ✅ Export logs for compliance

**Logged Actions:**
- RLS policy creation/deletion
- User assignments
- CLS taxonomy creation/deletion
- Policy tag creation/deletion
- Tag application/removal

**[IMAGE PLACEHOLDER: Screenshot showing Audit Logs dashboard with recent activities]**

---

## **5. User Guide**

### **5.1 Accessing the Application**

1. Open the Cloud Run Service URL in your browser
2. The application loads with a navigation menu on the left

**[IMAGE PLACEHOLDER: Screenshot showing application home page]**

---

### **5.2 Working with Row-Level Security (RLS)**

#### **Creating a User-Based Policy**

1. Navigate to: **Row Level Security → Create Policy Users**
2. Fill in the policy details:
   - Policy Name
   - Project ID
   - Dataset ID
   - Table Name
   - Field ID
3. Click **Create Policy**

**[IMAGE PLACEHOLDER: Screenshot showing Create Policy Users form]**

#### **Assigning Users to Policies**

1. Navigate to: **Row Level Security → Assign Users to Policy**
2. Select the policy
3. Select RLS Type (username, service account, or domain)
4. Enter the filter value and user identifier
5. Click **Assign**

**[IMAGE PLACEHOLDER: Screenshot showing Assign Users interface]**

---

### **5.3 Working with Column-Level Security (CLS)**

#### **Creating a Taxonomy**

1. Navigate to: **Column Level Security → Manage Taxonomies**
2. Click **Create New Taxonomy**
3. Enter:
   - Display Name
   - Description (optional)
4. Click **Create**

**[IMAGE PLACEHOLDER: Screenshot showing Create Taxonomy form]**

#### **Creating Policy Tags**

1. Navigate to: **Column Level Security → Manage Policy Tags**
2. Select a taxonomy
3. Click **Create New Tag**
4. Enter:
   - Tag Display Name
   - Description (optional)
   - Parent Tag (optional, for nested tags)
5. Click **Create**

**[IMAGE PLACEHOLDER: Screenshot showing Create Policy Tag form]**

#### **Applying Tags to Columns**

1. Navigate to: **Column Level Security → Apply Tags to Columns**
2. Select Dataset and Table
3. View the list of columns with their current tags
4. For each column:
   - Select a tag from the dropdown
   - Click **Apply** to add/update the tag
   - Click **Remove** to remove the tag

**[IMAGE PLACEHOLDER: Screenshot showing Apply Tags interface with tagged columns]**

---

### **5.4 Monitoring with Audit Logs**

1. Navigate to: **Audit Logs**
2. View the dashboard showing:
   - Recent activities
   - Success/failure statistics
   - Filter options
3. Use filters to find specific operations:
   - Filter by Action (APPLY_TAG, REMOVE_TAG, CREATE_POLICY, etc.)
   - Filter by User
   - Filter by Status (SUCCESS/FAILED)
   - Filter by Date Range

**[IMAGE PLACEHOLDER: Screenshot showing Audit Logs with filters applied]**

---

## **6. Security Best Practices**

### **6.1 Row-Level Security**

- ✅ Always test RLS policies in a development environment first
- ✅ Document all policies and their business justification
- ✅ Regularly review and audit policy assignments
- ✅ Use group-based policies for easier management at scale

### **6.2 Column-Level Security**

- ✅ Design a clear taxonomy structure before implementation
- ✅ Use hierarchical tags for better organization
- ✅ Document which columns contain sensitive data
- ✅ Regularly audit tag applications
- ✅ **Never apply CLS tags to RLS control tables** (policies, policies_filters, audit_logs)

### **6.3 Audit Logging**

- ✅ Regularly review audit logs for suspicious activity
- ✅ Export logs periodically for compliance
- ✅ Set up alerts for failed operations
- ✅ Retain logs according to your compliance requirements

---

## **7. Troubleshooting**

### **7.1 Common Issues**

#### **Issue: Cannot create policies**
**Solution:** Verify the Service Account has `bigquery.admin` role

#### **Issue: Cannot create taxonomies**
**Solution:** Verify the Service Account has `datacatalog.admin` role

#### **Issue: Tags not being removed**
**Solution:** This was a known issue, fixed in v2.0. Ensure you're using the latest version.

#### **Issue: Audit logs not appearing**
**Solution:** Verify the `audit_logs` table exists and has the correct schema

---

### **7.2 Viewing Logs**

To view application logs in Cloud Shell:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=rls-cls-manager" --limit 50 --format="value(textPayload)"
```

**[IMAGE PLACEHOLDER: Screenshot showing Cloud Run logs in Cloud Console]**

---

## **8. MVP Feature Requirements**

### **8.1 Implemented Features (v2.0)**

#### **✅ 8.1.1 Audit Logging**
- Comprehensive logging of all user actions
- Timestamps, user identities, and change tracking
- UI for reviewing and filtering logs
- Export capabilities

#### **8.1.2 Authentication Integration - TO BE IMPLEMENTED**
- **Objective:** Securely authenticate users using GCP credentials
- **Requirements:**
  - Integrate with GCP IAM for authentication
  - Use authenticated user's credentials for all operations
  - Enforce actions under user's GCP permissions

#### **8.1.3 Role-Based Access Control (RBAC) - TO BE IMPLEMENTED**
- **Objective:** Granular permission system
- **Requirements:**
  - Define user roles (Administrator, Editor, Viewer)
  - Assign roles to users
  - Enforce permission checks
  - Manage roles from the application

---

## **9. Architecture Overview**

### **9.1 Components**
```
┌─────────────────────────────────────────────────────────┐
│                     Cloud Run                           │
│  ┌───────────────────────────────────────────────────┐ │
│  │         RLS & CLS Security Manager                │ │
│  │                                                   │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │ │
│  │  │   RLS    │  │   CLS    │  │  Audit Logs  │  │ │
│  │  │  Module  │  │  Module  │  │    Module    │  │ │
│  │  └──────────┘  └──────────┘  └──────────────┘  │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
           │                    │                │
           ▼                    ▼                ▼
    ┌──────────────┐    ┌──────────────┐  ┌──────────────┐
    │   BigQuery   │    │ Data Catalog │  │   BigQuery   │
    │ RLS Control  │    │  Taxonomies  │  │  Audit Logs  │
    │    Tables    │    │  Policy Tags │  │    Table     │
    └──────────────┘    └──────────────┘  └──────────────┘
```

---

## **10. Version History**

### **v2.0 - November 2025**
- ✅ Added Column-Level Security (CLS) module
- ✅ Added Audit Logging system
- ✅ Integrated RLS and CLS in single application
- ✅ Fixed policy tag removal issue
- ✅ Enhanced logging with Python logging module

### **v1.0 - March 2025**
- ✅ Initial release with RLS functionality

---

## **11. Support and Contributing**

### **11.1 Getting Help**

For issues or questions:
- Check the Troubleshooting section
- Review Cloud Run logs
- Contact your GCP administrator

### **11.2 Contributing**

This is a prototype application. Contributions and improvements are welcome.

---

## **12. License and Disclaimer**

**IMPORTANT DISCLAIMER:**

This application is a prototype intended for **experimental purposes only**. It is **not suitable for production environments**. The software is provided "as is," without any warranties, express or implied, including but not limited to merchantability, fitness for a particular purpose, and non-infringement. Google and the developers shall not be liable for any claims, damages, or liabilities arising from the use of this software. Use of this tool is at your own discretion and risk. Google is not responsible for the functionality, reliability, or security of this prototype.

---

## **Appendix A: Complete Command Reference**

### **Service Account Setup**
```bash
# Create service account
gcloud iam service-accounts create sa-rls-cls-manager --display-name="RLS CLS Manager"

# Get email
gcloud iam service-accounts list --project=YOUR_PROJECT --filter="displayName:sa-rls-cls-manager" --format="value(email)"

# Grant roles
gcloud projects add-iam-policy-binding YOUR_PROJECT --member="serviceAccount:SA_EMAIL" --role="roles/bigquery.admin"
gcloud projects add-iam-policy-binding YOUR_PROJECT --member="serviceAccount:SA_EMAIL" --role="roles/datacatalog.admin"
gcloud projects add-iam-policy-binding YOUR_PROJECT --member="serviceAccount:SA_EMAIL" --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding YOUR_PROJECT --member="serviceAccount:SA_EMAIL" --role="roles/run.invoker"
gcloud projects add-iam-policy-binding YOUR_PROJECT --member="serviceAccount:SA_EMAIL" --role="roles/iam.serviceAccountTokenCreator"
```

### **Dataset and Tables Creation**
```bash
# Create dataset
bq mk --dataset --location=us-central1 YOUR_PROJECT:rls_manager

# Create tables (run SQL commands from section 3.4)
```

### **Deployment**
```bash
# Clone repository
cd $HOME
git clone https://github.com/lucascarvalhal/RLS_CLS_Manager_Integrated.git
cd RLS_CLS_Manager_Integrated

# Edit config.py (update PROJECT_ID and LOCATION)

# Deploy
gcloud run deploy rls-cls-manager --region=us-central1 --source . --platform managed --service-account="SA_EMAIL" --port=8080 --memory=1Gi --timeout=300 --allow-unauthenticated --project=YOUR_PROJECT
```

---

**🎉 Setup Complete! Your RLS & CLS Security Manager is now ready to use!**
