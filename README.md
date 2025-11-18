# **GenAI Security Manager Setup Guide - v1-Mar-2025**

## **1. Introduction**

This guide outlines the steps required to deploy the **GenAI4SAP Security Manager** application within your environment.

**Important Notice:**

**This application is a prototype intended for experimental purposes only. It is not suitable for production use. This software is provided "as is," without any warranties, express or implied, including but not limited to merchantability, fitness for a particular purpose, and non-infringement. Google and the developers shall not be liable for any claims, damages, or other liabilities arising from the use of this software. Use this tool at your own risk. Google is not responsible for its functionality, reliability, or security.**

## **2. Prerequisites**

### **2.1 Framework Understanding**

Successful deployment relies on a solid understanding of:

* Your company's business rules and requirements.
* The functional aspects of your workload (e.g., SAP, Salesforce).
* Google Cloud fundamentals and products.

### **2.2 Required Knowledge**

Before proceeding, ensure you are familiar with:

* Google Cloud Platform [fundamentals](https://www.coursera.org/lecture/gcp-fundamentals/welcome-to-gcp-fundamentals-I6zpd).
* Navigating the Cloud Console, [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell), and [Cloud Shell Editor](https://cloud.google.com/shell/docs/editor-overview).
* [BigQuery](https://cloud.google.com/bigquery/docs/introduction) fundamentals.
* [Identity and Access Management](https://cloud.google.com/iam/docs/) fundamentals.

## **3. Solution Deployment**

### **3.1 Project Setup**

**Note:** When copying commands, ensure no extra blank lines are included, as they can cause errors.

### **3.2 Required Google Cloud Components**

The following Google Cloud components are necessary:

* Google Cloud Project.
* BigQuery instance and datasets.
* Cloud Run.
* Service Account.
* Default Artifact Repository.

### **3.3 Service Account Configuration**

For running the application on Cloud Run, a dedicated Service Account with the required permissions is recommended. If a new Service Account is needed, use the following commands:

**Create and Grant Service Account Roles:**

**Important:** Replace the `{value}` placeholders with your specific parameters.

**Service Account:**

1.  **Create the Service Account:**
    ```bash
    gcloud iam service-accounts create {service_account_name} --display-name="{display_name}"
    ```

    ![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/CreateServiceAccount.png)

2.  **Get Service Account Email:**
    ```bash
    gcloud iam service-accounts list --project={project_id} --filter="displayName:{service_account_name}" --format="value(email)"
    ```

    ![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/ListServiceAccount.png)

3.  **Granting the Requeried Roles:**
    ```bash
    gcloud projects add-iam-policy-binding {project_id} --member="serviceAccount:{service_account_email}" --role="roles/bigquery.admin"
    gcloud projects add-iam-policy-binding {project_id} --member="serviceAccount:{service_account_email}" --role="roles/run.invoker"
    gcloud projects add-iam-policy-binding {project_id} --member="serviceAccount:{service_account_email}" --role="roles/iam.serviceAccountTokenCreator"
    ```

    ![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/GratingSARoles.png)

### **3.4 BigQuery Dataset and Table Creation**

1.  **Create the `rls_security` dataset:**
    
    ![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/CreateDataset.png)
    - 
2.  **Create the following tables within the `rls_security` dataset:**
    
    **`rls_security.policies` table:**
    
    SQL
    
    ```
    CREATE TABLE `your-project-id.rls_security.policies` (
        policy_id STRING DEFAULT GENERATE_UUID() NOT NULL,
        policy_type STRING NOT NULL,
        policy_name STRING NOT NULL,
        project_id STRING NOT NULL,
        dataset_id STRING NOT NULL,
        table_name STRING NOT NULL,
        field_id STRING NOT NULL,
        group_email STRING
    );
    
    ```
    
    **`rls_security.policies_filters` table:**
    
    SQL
    
    ```
    CREATE TABLE `your-project-id.rls_security.policies_filters` (
        id STRING DEFAULT GENERATE_UUID() NOT NULL,
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
        domain STRING
    );
    
    ```
    

### **3.5 Cloning the GitHub Repository**

Use Cloud Shell to clone the GitHub repository:

Bash

```
cd $HOME
git clone https://github.com/GenAI4Data/GenAI4Data_Sec_Manager.git
```

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/Gitclone.png)

### **3.6 Application Configuration**

Open the `config.py` file in the Cloud Editor and insert your specific configuration values.

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/ConfigPy.png)

### **3.7 Application Deployment**

**Important:** Replace the `{value}` placeholders with your specific parameters.

Navigate to the `GenAI4Data_Sec_Manager` directory:

```bash
cd $HOME/GenAI4Data_Sec_Manager

gcloud beta run deploy {cloud_run_app_name} --region={region_id} --source . --execution-environment=gen2 --service-account="{service_account_email}" --port=8080 --cpu=2 --memory=2Gi --min-instances=1 --allow-unauthenticated --project={your_project_id}

```

![image](https://raw.githubusercontent.com/GenAI4Data/GenAI4Data_Sec_Manager/refs/heads/main/docs/images/Deploy.png)

## **4. GenAI Security Manager - Minimum Viable Product (MVP) Features**

### **4.1. Purpose, Scope, and Disclaimer**

This document outlines the core features for the GenAI Security Manager MVP, focusing on the creation and management of BigQuery Row-Level Security (RLS) policies.

**IMPORTANT DISCLAIMER:**

This application is a prototype intended for **experimental purposes only**. It is **not suitable for production environments**. The software is provided "as is," without any warranties, express or implied, including but not limited to merchantability, fitness for a particular purpose, and non-infringement. Google and the developers shall not be liable for any claims, damages, or liabilities arising from the use of this software. Use of this tool is at your own discretion and risk. Google is not responsible for the functionality, reliability, or security of this prototype.

### **4.2. MVP Feature Requirements**

The following features are considered essential for the Minimum Viable Product (MVP) and are to be implemented by customers or partners:

#### **4.2.1. Audit Logging**

* **Objective:** Maintain a comprehensive record of all user actions and policy modifications within the application.
* **Requirements:**
    * Track all user interactions, including but not limited to:
        * Policy creation.
        * Policy deletion.
        * Policy updates (e.g., adding, modifying, or removing policy conditions).
        * User logins and logouts.
    * Record timestamps, user identities, and specific changes made.
    * Provide a mechanism to review and export audit logs.

#### **4.2.2. Authentication Integration with Google Cloud Platform (GCP)**

* **Objective:** Securely authenticate users and authorize actions using GCP user credentials.
* **Requirements:**
    * Integrate with GCP's Identity and Access Management (IAM) for user authentication during application login.
    * Utilize the authenticated user's GCP credentials to execute all commands related to BigQuery RLS policy management.
    * Ensure that all actions are performed under the context of the user's GCP permissions.

#### **4.2.3. Role-Based Access Control (RBAC)**

* **Objective:** Implement a granular permission system to control user access and actions within the application.
* **Requirements:**
    * Define distinct user roles with specific permissions (e.g., "Policy Administrator," "Policy Editor," "Policy Viewer").
    * Allow administrators to assign roles to users.
    * Enforce permission checks for all actions, such as:
        * Creating policies (e.g., restricted to "Policy Administrator").
        * Modifying policy conditions (e.g., granted to "Policy Editor").
        * Viewing Policies (e.g. granted to "Policy Viewer").
    * Provide a way to manage roles and permission from the application.


## **5. User Guide**

The user guide is provided here: [User Guide](https://github.com/GenAI4Data/GenAI4Data_Sec_Manager/blob/main/docs/USERGUIDE.md)