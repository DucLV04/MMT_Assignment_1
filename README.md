

# 📝Assignment 1- Implement HTTP server

## Task 1: HTTP server with cookie session
- ✅ Cookie-based authentication
- ✅ Session management
- ✅ Access control for protected resources
## Task 2: Implement hybrid chat application
- Client-Server paradigm
  - ✅ Peer registration
  - ✅ Tracker update
  - ✅ Peer discovery
  - ✅ Connection setup
- Peer-to-Peer paradigm
  - ✅ Broadcast connection
  - ✅ Direct peer communication
- Channel management
  - ✅ Channel listing
  - ✅ Message display
  - ✅ Message submission
## Task 3: Put It All Together
#### 🏗️ System Architecture
```
┌─────────────────────────────────────────────────┐                                                  
│          HTTP Server Layer                      │                                                  
│  ┌──────────┐        ┌─────────────┐            │                                                             
│  │  Proxy   │───────►│   Backend   │            │                                              
│  │  :8080   │        │   :9000     │            │
│  └──────────┘        └─────────────┘            │
└─────────────────────────────────────────────────┘
```
#### 🚀 How to run
- ##### Step 1: Setup
  - Open some virtual machines, connect them to a same subnet
  - Choose 1 virtual machine to be the tracker 
- ##### Step 2: Start Backend Server
  - Run sampleapp in each virtual machine by typing this line in terminal
```bash
python start_sampleapp.py --server-ip <your-tracker-ip> --server-port 8000
```
- #### Step 3: Open your Browser
  -   Open a browser (Incognito mode recommended)
  - Visit: `http://<your-computer-ip>:8000/`
     - ❌  401 Unauthorized (no cookie yet)
  - Visit: `http://<your-computer-ip>:8000/login.html`
     - ✅ Shows login form
    Login with:
         - Username: `admin`
         - Password: `password`
     - ❌ InValid: 401 Unauthorized (no cookie yet)
     - ✅ Valid: Redirect to `http://<your-computer-ip>:8000/`
  - Visit again: `http://<your-computer-ip>:8000/`
     - ✅ 200 OK (valid cookie)

    


