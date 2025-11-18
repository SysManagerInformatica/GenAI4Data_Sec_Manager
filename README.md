# **RLS & CLS Security Manager Setup Guide - v2.0-Nov-2025**

## **1. Introduction**

This guide outlines the steps required to deploy the **RLS & CLS Security Manager** application within your environment.

This enhanced version includes:
- **Row-Level Security (RLS)** - Control access at the row level
- **Column-Level Security (CLS)** - Control access at the column level using Policy Tags
- **Audit Logging** - Track all security operations and changes

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
git clone https://github.com/SysManagerInformatica/GenAI4Data_Sec_Manager.git
```

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/Gitclone.png)

---

### **3.7 Application Configuration**

Navigate to the cloned directory and open the `config.py` file:
```bash
cd $HOME/GenAI4Data_Sec_Manager
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

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/ConfigPy.png)

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
cd $HOME/GenAI4Data_Sec_Manager

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

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/Deploy.png)

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

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/Deploy.png)

---

## **4. Application Features**

### **4.1 Row-Level Security (RLS)**

Manage BigQuery Row-Level Security policies to control data access at the row level.

**Features:**
- Create RLS policies (User-based and Group-based)
- Assign users to policies
- Assign filter values to groups
- View and manage existing policies

![image](https://github.com/SysManagerInformatica/GenAI4Data_Sec_Manager/blob/d0092a826b0c52d144af35c0622113c9b2c1629e/docs/images/ViewRLS.png)

---

### **4.2 Column-Level Security (CLS) - NEW!**

Manage BigQuery Column-Level Security using Data Catalog Policy Tags.

![image](https://github.com/SysManagerInformatica/GenAI4Data_Sec_Manager/blob/de78ff2c05d77f847a6ec7d83d867f07d2599e2a/docs/images/ViewCLS.png)

#### **4.2.1 Manage Taxonomies**

Create and manage Data Catalog taxonomies.

**Features:**
- Create new taxonomies
- View existing taxonomies
- Delete taxonomies

#### **4.2.2 Manage Policy Tags**

Create and organize policy tags within taxonomies.

**Features:**
- Create new policy tags
- Create nested/hierarchical tags
- View tag structure
- Delete tags

#### **4.2.3 Apply Tags to Columns**

Apply policy tags to BigQuery table columns.

**Features:**
- Browse datasets and tables
- View column schemas
- Apply tags to columns
- Remove tags from columns
- View tagging statistics
---

### **4.3 Audit Logging - NEW!**

Track all security operations and changes.

**Features:**
- Real-time activity dashboard
- Filter logs by action, user, status, date
- View detailed operation information
- Export logs for compliance

**Logged Actions:**
- RLS policy creation/deletion
- User assignments
- CLS taxonomy creation/deletion
- Policy tag creation/deletion
- Tag application/removal

![image](https://github.com/SysManagerInformatica/GenAI4Data_Sec_Manager/blob/6752678c6f6f1f66b64dc97d4bcad1d594535434/docs/images/ViewLogs.png)


---

**Setup Complete! Your RLS & CLS Security Manager is now ready to use!**

## **5. User Guide**

[User Guide](docs/USERGUID.md)


