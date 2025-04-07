# 🚀 Getting Started

## 1. Prerequisites

Before running this project, ensure you have the following installed:

- **Docker Desktop (Recommended)**
  - Includes both Docker Engine and Docker Compose.
  - Available for macOS, Windows, and Linux.
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## 2. Clone the Project

You can download the project in one of two ways:

### Option 1: Download ZIP
1. Visit the repository: [https://github.com/cjkjacob/msc_project](https://github.com/cjkjacob/msc_project)
2. Click the green **Code** button.
3. Select **Download ZIP**.
4. Extract the ZIP file to a convenient location on your machine.

### Option 2: Use Git (if installed)
```bash
git clone https://github.com/cjkjacob/msc_project.git
cd msc_project-main
```

---

## 3. Build and Run the Application

Once inside the project directory, open a terminal and run:

```bash
docker compose up --build
```

This command will:
- Build Docker images for both the **Django backend** and **Vue frontend**.
- Launch **three Django backend instances** on ports `8000`, `8001`, and `8002`.
- Start the **Vue frontend** on port `5173`.

---

## 4. Access the Application

Once everything is up and running, visit:

👉 [http://localhost:5173](http://localhost:5173)

This will take you to the frontend interface.

---

# 👤 User Registration & Setup

Once the application is running, you'll need to register the necessary users to access the platform.

---

## 1. Create a Django Superuser (Optional)

If you're starting from scratch **without an existing database instance**, you'll need to create a Django superuser for administrative access.

To do this, run the following command in your terminal:

```bash
docker exec -it django_backend_8000 python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

> **Tip:**  
> If you're using the original preconfigured database, you can log in with:
> - **Username:** `admin`  
> - **Password:** `admin123`

You can then access the Django admin dashboard at:

```
http://localhost:8000/admin
```

---

## 2. Register Users via the Frontend

Open the Vue frontend in your browser:

```
http://localhost:5173
```

Click on **Register** and follow the instructions for each user type.

---

### 👉 Register a Validator

1. Fill out the registration form with the required details.
2. Select the **role** as `Validator`.
3. Make sure the passwords match.
4. Click **Register**.
5. ✅ **Important:** Save the downloaded **private key file** securely — this is required for validating efforts.

---

### 🎓 Register a Student

1. Repeat the same steps as for the validator.
2. Select the **role** as `Student`.
3. Save the **private key file** securely — it is needed to submit efforts to the blockchain.

---

You can repeat this process to create as many validators and students as needed.

---


# 🎓 Student Workflow

Once users are registered, you can access the platform via the frontend at:

```
http://localhost:5173
```

---

## 🔐 Logging In

1. Navigate to the **Login** page.
2. Enter your **username** and **password** from registration.
3. Click **Login** to access your dashboard.

---

## 🪪 Uploading Your Private Key

After logging in, you must upload your **private key file** to sign and submit efforts.

To do this:

1. Click on **Wallet** from the navigation bar.
2. Use the file uploader to submit the **private key file** downloaded during registration.

> ⚠️ **Note:**  
> If your private key is not yet uploaded, the system will automatically redirect you to the Wallet page when attempting actions that require signing (like submitting efforts).

---

## 📤 Submitting an Effort

To submit a new effort:

1. Navigate to the **Submit Effort** page.
2. Fill out the form with the following fields:
   - **Task ID** – Title of your effort.
   - **Effort Type** – Choose from:
     - `Learning`
     - `Mental`
     - `Physical`
   - **Evidence File** – Upload supporting evidence in `.jpeg`, `.png`, or `.pdf` format.
   - **Effort Score** – Must be **20 or above** to be valid.
   - **Validator ID** – The **username** of the validator assigned to verify this effort.  
     > Example: If using the default database, use `validator_01`.

3. Click **Submit**.

> ✅ If the effort is submitted correctly, it will enter the **pending queue** for validator approval.

---

## 🧭 Exploring the Platform

After submitting an effort, students can explore the following sections:

- **Leaderboard**  
  View rankings of users based on total tokens and validated efforts.

- **Wallet**  
  View your current token balance and transaction history.

- **Efforts**  
  See all submitted efforts across the platform.  
  You can filter by **username** and **effort type**.

- **Blockchain**  
  Inspect the blockchain ledger — including effort data, timestamps, and block hashes.

- **Profile**  
  View your username, role, public key, and a list of all your **approved efforts**.

---

# 🛡️ Validator Workflow

Once you've registered or logged in as a **validator**, you can begin verifying and managing submitted efforts on the platform.

> If you're using the original preconfigured database, a default validator account is available:
>
> - **Username:** `validator_01`  
> - **Password:** `validate`

---

## 🔐 Logging In as a Validator

1. Visit `http://localhost:5173` and click on **Login**.
2. Enter your **validator credentials**.
3. Click **Login** to enter your dashboard.

---

## 🗝️ Uploading the Private Key

Just like students, validators **must upload their private key** before performing any signing or approval actions.

- You’ll be prompted automatically inside the **Validator Dashboard** if not already uploaded.
- Navigate to **Validator Dashboard** in the sidebar.
- Upload the private key file you saved during registration.

---

## ✅ Approving or ❌ Rejecting Efforts

Inside the **Validator Dashboard**, you can:

- 🔍 View all **pending efforts**
- 📄 See **submission details** and attached **evidence files**
- ✅ **Approve** valid efforts with one click
- ❌ **Reject** invalid or insufficient efforts — you must provide a **rejection reason**

> 🧾 **Tip:**  
> Evidence files (e.g. PDFs, images) can be previewed or downloaded for verification directly from the dashboard.

---

## 📊 Additional Features for Validators

Validators also have access to the following views:

- **Blockchain**  
  Inspect the full chain of approved efforts — complete with hashes, metadata, and block info.

- **Efforts**  
  View the full effort database.  
  Use filters to refine by **username** or **effort type**.

- **Leaderboard**  
  See the platform rankings based on total effort score and tokens earned.

---

## 🔒 Session Management

To maintain platform security:

- You must be **logged in** to access any student or validator functionality.
- If your session token expires (usually after ~15 minutes of inactivity), you’ll be **automatically redirected** to the login screen.
- After logging in again, you will be required to **re-upload your private key** to enable effort signing or validation actions.

---

# 🧠 Admin Access & Stopping the Platform

---

## 🛑 Stopping the Platform

To stop all running services (including all Django servers, the Vue frontend, and any supporting containers), run the following command **from the root project directory**:

```bash
docker compose down
```

This will gracefully shut down all services defined in your `docker-compose.yml` file.

---

## 🔐 Accessing the Django Admin Panel

You can use the Django Admin Panel for backend management and manual inspection.

To access it:

1. Open your browser and go to:  
   `http://localhost:8000/admin`

2. Log in using the Django superuser credentials.

> If you're using the original preconfigured database:
> - **Username:** `admin`  
> - **Password:** `admin123`

---

## 🛠️ Admin Features

Once inside the admin dashboard, you can:

- 👥 **Manage users** — inspect roles, usernames, and wallet keys.
- 📁 **Review all pending efforts**, including uploaded evidence.
- 🧾 **Access and inspect** all approved or rejected efforts.
- 🪙 **View token allocations and effort rewards**.
- ⚙️ **Manually approve/reject** or modify entries (for troubleshooting or special overrides).

> 🧩 The admin panel is a powerful tool and should be used **only by trusted administrators**.


---

# 🐞 Troubleshooting Guide

## 📁 Project Structure Overview

A quick overview of how this project is laid out:

```
MSC_PROJECT/
│
├── frontend/             # Vue.js frontend with Vite
│   └── Dockerfile        # Frontend Docker build file
│
├── proof_of_effort/      # Django backend application
│   ├── blockchain/       # Blockchain app logic and models
│   └── Dockerfile        # Backend Docker build file
│   └── .env              # Backend environment configuration
│
├── requirements.txt      # Django backend dependencies
├── docker-compose.yml    # Multi-container Docker setup
└── README.md             # ← You're here!
```

---

## 🌍 Cross-Origin Configuration (CORS)

To allow the frontend to communicate with the backend securely, **Cross-Origin Resource Sharing (CORS)** is configured in the Django settings.

By default, this project allows connections from:

```
http://localhost:5173
```

If you change ports or deploy this to a different domain (e.g., on a server or cloud), be sure to update the following settings in `proof_of_effort/.env` or `settings.py`:

- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

> 🔐 Failing to update these may result in blocked API requests or CSRF errors in production.

---

## 🧪 Testing the System (Manual Checklist)

After setup, here’s a quick checklist to verify everything is working as expected:

| Test | Description |
|------|-------------|
| ✅ Register Student and Validator | Make sure both roles can be created successfully. |
| ✅ Upload Private Key | Each user should be able to upload their private key securely after logging in. |
| ✅ Submit an Effort | Students can submit an effort with valid file types and scores. |
| ✅ Approve / Reject | Validators can approve or reject efforts with clear feedback. |
| ✅ Leaderboard View | Leaderboard updates as students earn tokens. |
| ✅ Blockchain View | Blockchain reflects all validated efforts. |

---

## Common Errors

### ⚠️ Frontend not accessible?

- Check that port `5173` is open.
- Ensure the frontend container is **running**:
  ```bash
  docker ps
  ```

### ⚠️ Vite not found?

- Make sure the frontend `Dockerfile` uses **Node 18+**.
- Use:
  ```dockerfile
  CMD ["npx", "vite"]
  ```

### ⚠️ Docker volume issues?

- Try resetting volumes:
  ```bash
  docker compose down -v
  ```

### ⚠️ Effort not submitting?

- Ensure you've **uploaded the private key** under Wallet.
- Double-check the **validator username** is accurate.
- Score should be **≥ 20**.
- Only `.jpeg`, `.png`, or `.pdf` are accepted as evidence.


_Last updated: **April 7, 2025**_

Made with 💡 by **cjkjacob**