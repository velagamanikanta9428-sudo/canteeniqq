=================================================================
         CanteenIQ -- Smart Canteen Pre-Order System
=================================================================

HOW TO RUN
----------
Step 1: Install Python packages (only once)
        pip install flask flask-cors

Step 2: Start the server
        python server.py

Step 3: Open browser and go to
        http://localhost:5000

Done! The full app is live.

-----------------------------------------------------------------
FILES IN THIS PROJECT
-----------------------------------------------------------------

  server.py            Main Python backend server
  canteeniq.html       Frontend web application
  README.txt           This guide

Notepad files (auto-created & updated live):
  users.txt            All registered users
  orders.txt           All placed orders
  canteeniq_data.txt   Combined users + orders report

-----------------------------------------------------------------
NOTEPAD FILES -- WHAT IS STORED
-----------------------------------------------------------------

  users.txt
    - User #, Name, Email, Student ID
    - Department, Year/Batch
    - Registration Date & Time
    - Total Orders, Total Spent, Reward Points

  orders.txt
    - Order #, Order ID, Item Name
    - Student Name, Student ID, Department
    - Pickup Slot, Amount, Payment Mode
    - Order Date & Time, Status (PENDING/READY/DELIVERED)

  canteeniq_data.txt
    - Complete combined report
    - Section 1: All Registered Users
    - Section 2: All Orders placed
    - Auto-updates every time someone registers or orders

-----------------------------------------------------------------
WHEN DO FILES UPDATE?
-----------------------------------------------------------------
  - users.txt       --> Updates instantly when a new user registers
  - orders.txt      --> Updates instantly when an order is placed
                        or its status changes (pending/ready/delivered)
  - canteeniq_data  --> Updates at the same time as above

Just open them in Notepad at any time to see latest data!

-----------------------------------------------------------------
ADMIN / OWNER LOGIN
-----------------------------------------------------------------
  Username : admin
  Password : canteen@2025

-----------------------------------------------------------------
IMPORTANT NOTES
-----------------------------------------------------------------
  - Passwords are NEVER stored in the .txt files (security)
  - All data also saved in users.json and orders.json (backup)
  - The server must be running for the app to work

=================================================================
