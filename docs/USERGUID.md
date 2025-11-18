# **RLS & CLS Security Manager User Guide - v2.0-Nov-2025**

## **Purpose, Scope and Background**

This guide describes the steps required to use the **RLS & CLS Security Manager Application** to create:
- **BigQuery Row-Level Security (RLS) Policies**
- **BigQuery Column-Level Security (CLS) with Policy Tags**
- **Comprehensive Audit Logging for compliance**

**IMPORTANT:**

**This application is a prototype and should be used for experimental purposes only. It is not intended for production use. This software is provided 'as is' without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall Google or the developers be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software. Google is not responsible for the functionality, reliability, or security of this prototype. Use of this tool is at your own discretion and risk.**

## **User Guide**

### **Understand the Framework**

A **successful deployment depends** on a good understanding of:

* Your **company's business rules and requirements**
* **Functional understanding** of the workload (e.g., SAP, Salesforce)
* Google Cloud fundamentals and products
* **Data classification and sensitivity levels** (for CLS)

**Before continuing with this guide, make sure you are familiar with:**

* Google Cloud Platform [fundamentals](https://www.coursera.org/lecture/gcp-fundamentals/welcome-to-gcp-fundamentals-I6zpd)
* How to navigate the Cloud Console, [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell) and [Cloud Shell Editor](https://cloud.google.com/shell/docs/editor-overview)
* Fundamentals of [BigQuery](https://cloud.google.com/bigquery/docs/introduction)
* Fundamentals of [Identity and Access Management](https://cloud.google.com/iam/docs/)

### **Prerequisites Knowledge**

#### **For RLS (Row-Level Security):**
* BigQuery access control patterns
* User and group management in GCP
* SQL filter expressions

#### **For CLS (Column-Level Security):**
* [Data Catalog](https://cloud.google.com/data-catalog/docs) fundamentals
* Policy Tags and Taxonomies concepts
* Column-level data classification

## **Part 1: Row Level Security (RLS)**

### **Create Row Level Security for User Assignment**

**Navigate to:** `Row Level Security → Create Policy Users`

**Required Fields:**
* **Policy Name:** Unique identifier for the policy (e.g., `sales_region_policy`)
* **Project ID:** Your GCP project ID
* **Dataset ID:** The BigQuery dataset name
* **Table Name:** The table to apply RLS
* **Field ID:** The column to filter on (e.g., `region`, `department`)

**Click** `Create Policy` to save.

### **Create Row Level Security for Group Assignment**

**Navigate to:** `Row Level Security → Create Policy Groups`

**Required Fields:**
* **Policy Name:** Unique identifier
* **Project ID:** Your GCP project ID
* **Dataset ID:** BigQuery dataset name
* **Table Name:** Target table
* **Field ID:** Column for filtering
* **Group Email:** Google Group email address

**Click** `Create Group Policy` to save.

### **Assign Users to Policies**

**Navigate to:** `Row Level Security → Assign Users to Policy`

**Steps:**
1. **Select the Policy** from the dropdown
2. **Choose RLS Type:**
   * `username` - Individual user email
   * `service_account` - Service account email
   * `domain` - Entire domain access
3. **Enter Filter Value:** The value to match (e.g., `Brazil`, `Sales`)
4. **Enter User Identifier:** Email or domain
5. **Click** `Assign User`

### **View and Manage Policies**

**Navigate to:** `Row Level Security → View Policies`

* View all active policies with configurations
* Filter by project, dataset, or table
* Delete policies when needed

## **Part 2: Column Level Security (CLS)**

### **Manage Taxonomies**

**Navigate to:** `Column Level Security → Manage Taxonomies`

**To Create a Taxonomy:**
1. **Click** `Create New Taxonomy`
2. **Enter Display Name:** Descriptive name (e.g., `PII_DATA`)
3. **Enter Description:** Purpose of the taxonomy
4. **Click** `Create Taxonomy`

**Available Taxonomies** are listed with options to view or delete.

### **Manage Policy Tags**

**Navigate to:** `Column Level Security → Manage Policy Tags`

**To Create Policy Tags:**
1. **Select a Taxonomy** from the dropdown
2. **Click** `Create New Tag`
3. **Enter Tag Display Name:** The tag identifier (e.g., `HIGH_SENSITIVE`)
4. **Enter Description:** What this tag protects
5. **Select Parent Tag:** (Optional) For hierarchical structure
6. **Click** `Create Tag`

**Example Tag Hierarchy:**
```
PII_DATA (Taxonomy)
├── HIGH_SENSITIVE
│   ├── SSN
│   ├── CREDIT_CARD
│   └── BANK_ACCOUNT
├── MEDIUM_SENSITIVE
│   ├── EMAIL
│   ├── PHONE
│   └── ADDRESS
└── LOW_SENSITIVE
    ├── NAME
    └── JOB_TITLE
```

### **Apply Tags to Columns**

**Navigate to:** `Column Level Security → Apply Tags to Columns`

**Steps to Apply Tags:**
1. **Select Dataset** from the dropdown
2. **Select Table** from the dropdown
3. **View the column list** with current tags
4. **For each column:**
   * **Select a policy tag** from the dropdown
   * **Click** `Apply` to add the tag
   * **Click** `Remove` to remove existing tag

**Tagging Statistics** are displayed showing:
* Total tables with tags
* Total columns protected
* Tag distribution across datasets

## **Part 3: Audit Logs**

### **View Audit Dashboard**

**Navigate to:** `Audit Logs`

**Dashboard displays:**
* **Recent activities** timeline
* **Success/failure** statistics
* **User activity** summary
* **Most common operations**

### **Filter and Search Logs**

**Available Filters:**
* **By Action:** 
  * `CREATE_POLICY` - RLS policy creation
  * `DELETE_POLICY` - RLS policy deletion
  * `ASSIGN_USER` - User assignment
  * `CREATE_TAXONOMY` - Taxonomy creation
  * `CREATE_TAG` - Policy tag creation
  * `APPLY_TAG` - Tag application
  * `REMOVE_TAG` - Tag removal
* **By User:** Filter by email address
* **By Status:** `SUCCESS` or `FAILED`
* **By Date Range:** Select start and end dates

### **Export Logs**

**Export Options:**
* **CSV Export:** Click `Export to CSV` and select date range
* **BigQuery Query:** Access directly from `rls_manager.audit_logs` table

## **Best Practices**

### **For RLS:**
* **Test policies** in development environment first
* **Use groups** for easier management at scale
* **Document business rules** for each policy
* **Regular audits** of user assignments
* **Use meaningful** policy names

### **For CLS:**
* **Design taxonomy structure** before implementation
* **Use hierarchical tags** for better organization
* **Never apply CLS tags** to RLS control tables
* **Regular review** of tag applications
* **Follow data classification** standards

### **For Audit Logs:**
* **Review logs weekly** for suspicious activity
* **Export logs monthly** for compliance
* **Set up alerts** for failed operations
* **Document incidents** when they occur
* **Retain logs** according to compliance requirements

## **Troubleshooting**

### **RLS Issues:**

**Problem:** Policy not working  
**Solution:** Verify service account has **`bigquery.admin`** role

**Problem:** Users see no data  
**Solution:** Check filter values match actual data in table

**Problem:** Policy creation fails  
**Solution:** Ensure table and field names are correct

**Problem:** Cannot delete policy  
**Solution:** Remove all user assignments first

### **CLS Issues:**

**Problem:** Cannot create taxonomies  
**Solution:** Verify **`datacatalog.admin`** role and Data Catalog API is enabled

**Problem:** Tags not appearing on columns  
**Solution:** Check if Data Catalog API is enabled in project

**Problem:** Cannot remove tags  
**Solution:** Fixed in v2.0 - ensure you're using latest version

**Problem:** Tags not enforced  
**Solution:** Check IAM fine-grained reader permissions

### **Audit Issues:**

**Problem:** No logs appearing  
**Solution:** Verify **`audit_logs`** table exists in **`rls_manager`** dataset

**Problem:** Missing operations  
**Solution:** Check service account permissions

**Problem:** Export failing  
**Solution:** Ensure sufficient BigQuery quota

## **Quick Reference**

### **Required IAM Roles for Service Account:**
* **`bigquery.admin`** - For RLS operations
* **`datacatalog.admin`** - For CLS taxonomy management
* **`bigquery.dataEditor`** - For applying tags to columns
* **`run.invoker`** - For Cloud Run invocation
* **`iam.serviceAccountTokenCreator`** - For authentication

### **Control Tables:**
* **`rls_manager.policies`** - RLS policy definitions
* **`rls_manager.policies_filters`** - User assignments and filters
* **`rls_manager.audit_logs`** - All security operations logs

### **Common Operations:**
```sql
-- View existing policies
SELECT * FROM `project.rls_manager.policies`;

-- View user assignments  
SELECT * FROM `project.rls_manager.policies_filters`;

-- Check recent audit logs
SELECT * FROM `project.rls_manager.audit_logs`
WHERE DATE(timestamp) = CURRENT_DATE()
ORDER BY timestamp DESC;
```

## **Version History**

### **v2.0 - November 2025**
* **Added Column-Level Security (CLS)** module
* **Added comprehensive Audit Logging** system
* **Integrated RLS and CLS** in single interface
* **Fixed tag removal** issues
* **Enhanced error handling** and validation

### **v1.0 - March 2025**
* **Initial release** with RLS functionality
* **User and group-based** policies
* **Basic policy** management

---

**End of User Guide**


