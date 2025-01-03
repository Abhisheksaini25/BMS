import mysql.connector
import random
import datetime
import re
'''
Batch 6:
Enrollment No - 0157CS221009
Name - Abhishek ku Saini
Branch - CSE
'''

'''
users ->  name, acc_no, dob, city, pass, contact, email, address
login ->  acc_no, balance, status
transaction ->  acc_no, type, to_from, amount, up_balance, trxn_time
'''

db = mysql.connector.connect(host="localhost", user="root", passwd="1991", database="banking_system")
cur = db.cursor()
user = ""
status = ""

def home():  #Login/Sign up page
    forgot = Forgot()
    print("***-Welcome to the sign up/login in page-***")
    while True:
        print("1- Create a account \n2- Login to account \n3- Forgot Account number \n4- Forgot Password \n5- Show users \n6- Exit")
        inp = input("Enter your choice: ")
        if inp == "1":
            create_account()
        elif inp == "2":
            login()
        elif inp == "3":
            print("What will you use for verification? \n1- Email \n2- Contact")
            tp = input("Enter your choice: ")
            if tp == "1":
                forgot.accno("email")
            elif tp == "2":
                forgot.accno("contact")
            else:
                print("Enter a valid choice")
        elif inp == "4":
            forgot.pwd()
        elif inp == "5":
            sql = "SELECT name from users order by name asc"
            cur.execute(sql)
            usr = cur.fetchall()
            a=1
            for i in usr:
                print(f"{a} -> {i[0][0].upper() + i[0][1:].lower()}")
                a+=1
            input("Press enter to continue")
        elif inp == "6":
            print("***-Thank you-***")
            db.close()
            break
        else:
            print("Enter a valid choice")

def create_account():  #account creation
    validate = Validation()
    print("***-Welcome to the create account page-***")
    name = validate.basic("name")
    dob = validate.dob()
    address = validate.basic("address")
    city = validate.basic("city")
    contact = validate.contact()
    email = validate.email()
    print('''criteria for password-
-> At least 8 characters long
-> Includes upper and lowercase letters
-> Contains at least one number (0-9)
-> Contains at least one special character (e.g., !@#$%^&*)
-> Should not contain spaces''')
    pwd = validate.password()
    acc = validate.acc_number()

    sql = "Insert into users values(%s, %s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql,(name,acc,dob,city,pwd,contact,email,address))
    db.commit()

    amt = validate.initial_balance()
    sql = "Insert into login values(%s, %s, %s)"
    cur.execute(sql,(acc,amt,"active"))
    db.commit()

    print(f"Your account has been created \nYour account number is {acc}")
    input("Press enter to continue")

    tranx_update(acc,"initial", "self", amt, amt)

class Forgot:
    def accno(self,tp):  #deals with forgotten acc number
        w = input(f"Enter your {tp}: ")
        if tp=="email":
            try:
                sql = "SELECT acc_no FROM users WHERE email=%s"
                cur.execute(sql,(w,))
                ac = cur.fetchone()[0]
            except Exception:
                print("no email found")
            else:
                print("Your account number is", ac)
                input("Press enter to continue")
        elif tp=="contact":
            try:
                sql = "SELECT acc_no FROM users WHERE contact=%s"
                cur.execute(sql, (w,))
                ac = cur.fetchone()[0]
            except Exception:
                print("no contact found")
            else:
                print("Your account number is", ac)
                input("Press enter to continue")
        home()

    def pwd(self):
        w = input("Enter your Account Number: ")
        try:
            sql = "SELECT pwd FROM users WHERE acc_no=%s"
            cur.execute(sql, (w,))
            ac = cur.fetchone()[0]
        except Exception:
            print("no account found")
        else:
            print(f"Your password for account number {w} is {ac}")
            input("Press enter to continue")


def login(a=0):   #login
    global user,status
    acc = input("Enter your account number: ")
    if a == 3:
        input("You have tried maximum time \nPress Enter to return to sign up page")
        home()
    try:
        sql = "SELECT pwd FROM users WHERE acc_no = %s"
        cur.execute(sql, (acc,))
        password = cur.fetchone()[0]
    except Exception:
        print("user does not exist")
        login(a+1)

    else:
        pwd = input("Enter your password: ")
        if password == pwd:
            sql = "SELECT name FROM users WHERE acc_no = %s"
            cur.execute(sql, (acc,))
            un = cur.fetchone()[0]
            user = acc
            sql = "SELECT status FROM login WHERE acc_no = %s"
            cur.execute(sql, (acc,))
            status = cur.fetchone()[0]
            print(f"***-Welcome {un}-***")
            login_page()
        else:
            print("Wrong password")
            login(a+1)


def login_page():  #login page
    global user,status
    check = Validation()
    while user:
        print("""0- show details     | 1- show balance 
2- show transaction | 3- credit amount
4- debit amount     | 5- transfer amount 
6- Change password  | 7- Activate/Deactivate account  
8- Update Profile   | 9- Logout""")
        inp = input("Enter your choice: ")
        if inp == "0":
            sql = "SELECT * FROM users WHERE acc_no = %s"
            cur.execute(sql, (user,))
            details = cur.fetchall()
            print(f"Account number: {details[0][1]}  | Name: {details[0][0]} \nDate Of Birth: {details[0][2]} | City: {details[0][3]} \nContact: {details[0][5]}       | Email: {details[0][6]} \nAddress: {details[0][7]}")
            input("Press enter to continue")
        elif inp == "1":
            sql = "SELECT balance FROM login WHERE acc_no = %s"
            cur.execute(sql, (user,))
            balance = cur.fetchone()[0]
            print(f"Your account balance is {balance}")
            press_enter = input("Press enter to continue")
        elif inp == "2":
            sql = "SELECT type,to_from,amount,up_balance,trxn_time,trxn_id FROM transaction WHERE acc_no = %s"
            cur.execute(sql, (user,))
            trnx = cur.fetchall()
            top = ["Type", "to/from", "amount", "balance", "transaction time"]
            c = [16,10,10,10,18]
            count =0
            print("|", end="")
            for i in top:
                print(i.center(c[count]), end="|")
                count += 1
            print()
            for i in trnx:
                print(f"|{i[0].center(16)}|{i[1].center(10)}|{i[2].center(10)}|{i[3].center(10)}|{i[4].center(18)}|")
            input("Press enter to continue")
        elif inp == "3":
            if check.activity(status):
                print("Your account is inactive")
                login_page()
            ip = input("Enter amount: ")
            sql = "SELECT balance FROM login WHERE acc_no = %s"
            cur.execute(sql, (user,))
            balance = cur.fetchone()[0]
            balance = str(int(balance) + int(ip))
            print(f"Your account balance is {balance}")
            sql = "UPDATE login SET balance = %s WHERE acc_no = %s"
            cur.execute(sql, (balance,user,))
            db.commit()
            tranx_update(user,"credit", "self", ip, balance)
            input("Press enter to continue")
        elif inp == "4":
            if check.activity(status):
                print("Your account is inactive")
                login_page()
            sql = "SELECT balance FROM login WHERE acc_no = %s"
            cur.execute(sql, (user,))
            balance = cur.fetchone()[0]
            ip = input("Enter amount: ")
            if int(balance) < int(ip):
                print("Insufficient balance")
            else:
                balance = str(int(balance) - int(ip))
                print(f"Your account balance is {balance}")
                sql = "UPDATE login SET balance = %s WHERE acc_no = %s"
                cur.execute(sql, (balance, user,))
                db.commit()
                tranx_update(user,"debit", "self", ip, balance)
            input("Press enter to continue")
        elif inp == "5":
            if check.activity(status):
                print("Your account is inactive")
                login_page()
            tr_acc = input("Enter the account number where you want to transfer: ")
            try:
                sql = "SELECT balance,status FROM login WHERE acc_no = %s"
                cur.execute(sql, (tr_acc,))
                tr_balance, tr_status = cur.fetchone()
                if check.activity(tr_status):
                    print("The account to which you want to transfer is inactive")
                    login_page()
            except Exception:
                print("Account does not exist")
            else:
                sql = "SELECT balance FROM login WHERE acc_no = %s"
                cur.execute(sql, (user,))
                balance = cur.fetchone()[0]
                tr_amount = input("Enter transfer amount: ")
                if int(balance) < int(tr_amount):
                    print("Insufficient balance")
                else:
                    balance = str(int(balance) - int(tr_amount))
                    print(f"Your account balance is {balance}")
                    sql = "UPDATE login SET balance = %s WHERE acc_no = %s"
                    cur.execute(sql, (balance, user,))

                    tr_balance = str(int(tr_balance) + int(tr_amount))
                    sql = "UPDATE login SET balance = %s WHERE acc_no = %s"
                    cur.execute(sql, (tr_balance, tr_acc,))

                    tranx_update(user,"transferred to", tr_acc, tr_amount, balance)
                    tranx_update(tr_acc,"transferred by", user, tr_amount, tr_balance)

                    db.commit()
                input("Press enter to continue")
        elif inp == "7":
            if status == "active":
                print("1- Deactivate your account \n2- Back")
                ip = input("Enter choice: ")
                if ip == "1":
                    print("You will not be able to do any tranx with your account")
                    password = input("Enter password to confirm deactivation: ")
                    sql = "SELECT pwd FROM users WHERE acc_no = %s"
                    cur.execute(sql, (user,))
                    pd = cur.fetchone()[0]
                    if pd == password:
                        sql = "UPDATE login SET status = %s WHERE acc_no = %s"
                        cur.execute(sql, ("inactive", user))
                        db.commit()
                        status = "inactive"
                        print("Your account has been deactivated")
                        input("Press enter to continue")
                    else:
                        print("Wrong password, your account is still active")
                        input("Press enter to continue")
            elif status == "inactive":
                print("1- Activate your account \n2- Back")
                ip = input("Enter choice: ")
                if ip == "1":
                    password = input("Enter password to confirm Activation: ")
                    sql = "SELECT pwd FROM users WHERE acc_no = %s"
                    cur.execute(sql, (user,))
                    pd = cur.fetchone()[0]
                    if pd == password:
                        sql = "UPDATE login SET status = %s WHERE acc_no = %s"
                        cur.execute(sql, ("active",user))
                        db.commit()
                        status = "active"
                        print("Your account has been Activated")
                        input("Press enter to continue")
                    else:
                        print("Wrong password, your account is still  inactive")
                        input("Press enter to continue")
        elif inp == "6":
            sql = "SELECT pwd FROM users WHERE acc_no = %s"
            cur.execute(sql, (user,))
            prev_pass = cur.fetchone()[0]
            new_pass = Validation.password(prev_pass)
            sql = "UPDATE users SET pwd = %s WHERE acc_no = %s"
            cur.execute(sql, (new_pass, user,))
            db.commit()
        elif inp == "8":
            update_profile()
        elif inp == "9":
            user=""
            status=""
            home()
        else:
            print("Enter a valid choice")

def update_profile():  #updates details
    solo_validate = Validation()
    while True:
        print("What do you want to update?")
        print("1- Name \n2- DOB \n3- Address \n4- City \n5- Contact \n6- Email \n7- Exit")
        ip = input("Enter your choice: ")
        if ip == "1":
            sql = "SELECT name FROM users WHERE acc_no = %s"
            cur.execute(sql, (user,))
            old_nm = cur.fetchone()
            new_nm = input("Enter new name: ")
            if old_nm == new_nm:
                print("Name already exists")
            else:
                sql = "UPDATE users SET name = %s WHERE acc_no = %s"
                cur.execute(sql, (new_nm, user,))
                db.commit()
                print("Your name has been updated")
                input("Press enter to continue")
        elif ip == "2":
            sql = "SELECT dob FROM user WHERE acc_no = %s"
            cur.execute(sql, (user,))
            old_dob = cur.fetchone()
            new_dob = solo_validate.dob()
            if old_dob == new_dob:
                print("Dob already exists")
            else:
                sql = "UPDATE users SET dob = %s WHERE acc_no = %s"
                cur.execute(sql, (new_dob, user,))
                db.commit()
                print("Your dob has been updated")
                input("Press enter to continue")
        elif ip == "3":  # might as well update the city
            sql = "SELECT address FROM users WHERE acc_no = %s"
            cur.execute(sql, (user,))
            old_address = cur.fetchone()
            new_address = input("Enter new address: ")
            if old_address == new_address:
                print("Address already exists")
            else:
                sql = "UPDATE users SET address = %s WHERE acc_no = %s"
                cur.execute(sql, (new_address, user,))
                db.commit()
                print("Your address has been updated")
                input("Press enter to continue")
        elif ip == "4":
            sql = "SELECT city FROM users WHERE acc_no = %s"
            cur.execute(sql, (user,))
            old_city = cur.fetchone()
            new_city = input("Enter new city: ")
            if old_city == new_city:
                print("City already exists")
            else:
                sql = "UPDATE users SET city = %s WHERE acc_no = %s"
                cur.execute(sql, (new_city, user,))
                db.commit()
                print("Your city has been updated")
                input("Press enter to continue")
        elif ip == "5":
            sql = "SELECT contact FROM users WHERE acc_no = %s"
            cur.execute(sql, (user,))
            old_contact = cur.fetchone()
            new_contact = solo_validate.contact()
            if old_contact == new_contact:
                print("Contact already exists")
            else:
                sql = "UPDATE users SET contact = %s WHERE acc_no = %s"
                cur.execute(sql, (new_contact, user,))
                db.commit()
                print("Your contact has been updated")
                input("Press enter to continue")
        elif ip == "6":
            sql = "SELECT email FROM users WHERE acc_no = %s"
            cur.execute(sql, (user,))
            old_email = cur.fetchone()
            new_email = solo_validate.email()
            if old_email == new_email:
                print("Email already exists")
            else:
                sql = "UPDATE users SET email = %s WHERE acc_no = %s"
                cur.execute(sql, (new_email, user,))
                db.commit()
                print("Your email has been updated")
                input("Press enter to continue")
        elif ip == "7":
            login_page()
        else:
            print("Enter a valid choice")

class Validation:  #validates various things

    def dob(self, fdate="%d-%m-%Y"):
        while True:
            dt = input("Enter your date of birth(dd-mm-yyyy): ")
            try:
                birthdate = datetime.datetime.strptime(dt, fdate)
                today = datetime.date.today()
                age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
                if age >= 14:
                    return dt
                else:
                    print("Your are too young")
            except ValueError:
                print("Enter a valid date")

    def basic(self,pa):
        while True:
            inp = input(f"Enter your {pa}: ")
            if len(inp)>2:
                return inp

    def contact(self):
        while True:
            ct = input("Enter your contact number: ")
            if not ct.isdigit() or len(ct) != 10:
                print("Enter a valid number")
            else:
                return ct

    def email(self):
        while True:
            eml = input("Enter your email: ")
            pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if re.match(pattern, eml):
                return eml
            else:
                print("Enter a valid email")

    def password(self,prev=""):
        while True:
            if len(prev)>2:
                pwd = input("Enter new password: ")
            else:
                pwd = input("Enter your password: ")
            if len(pwd) < 8:
                print("Your password must be at least 8 characters")
            elif not re.search(r'[A-Z]', pwd):
                print("Password must contain at least one uppercase letter")
            elif not re.search(r'[a-z]', pwd):
                print("Password must contain at least one lowercase letter")
            elif not re.search(r'\d', pwd):
                print("Password must contain at least one number")
            elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
                print("Password must contain at least one special character")
            elif re.search(r'\s', pwd):
                print("Password cannot contain spaces")
            elif pwd == prev:
                print("Password cannot be same as previous password")
            else:
                return pwd

    def acc_number(self):
        cur.execute("SELECT acc_no FROM users")
        users = cur.fetchall()
        while True:
            rng = random.randint(10000000,99999999)
            if rng not in users:
                return rng

    def initial_balance(self):
        while True:
            amt = int(input("Enter initial balance(minimum 2000): "))
            if amt < 2000:
                print("Your initial balance cannot be less than 2000.")
            else:
                return amt

    def activity(self,st):
        if st == "inactive":
            return True
        else:
            return False

def tranx_update(acc,typ, oth, amt, up_bal):  #transaction updater
    tm = datetime.datetime.now().strftime("%H:%M %d-%m-%Y")
    sql = "INSERT INTO transaction(acc_no, type, to_from, amount, up_balance, trxn_time) VALUES (%s, %s, %s, %s, %s, %s)"
    cur.execute(sql, (acc, typ, oth, amt, up_bal, tm))
    db.commit()

home()

''' -> for tables creation <-
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    name VARCHAR(50) NOT NULL,
    acc_no VARCHAR(10) PRIMARY KEY,
    dob VARCHAR(10),
    city VARCHAR(50),
    pwd VARCHAR(50),
    contact VARCHAR(10),
    email VARCHAR(100),
    address VARCHAR(300)
);
"""
create_login_table = """
CREATE TABLE IF NOT EXISTS login (
    acc_no VARCHAR(10) PRIMARY KEY,
    balance VARCHAR(20),
    status VARCHAR(10),
    FOREIGN KEY (acc_no) REFERENCES users(acc_no)
);
"""
create_transaction_table = """
CREATE TABLE IF NOT EXISTS transaction (
    trxn_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_no VARCHAR(10),
    type VARCHAR(20),
    to_from VARCHAR(10),
    amount VARCHAR(20),
    up_balance VARCHAR(20),
    trxn_time VARCHAR(20),
    FOREIGN KEY (acc_no) REFERENCES users(acc_no)
);
"""

cur.execute(create_users_table)
cur.execute(create_login_table)
cur.execute(create_transaction_table)

db.commit()
'''