import sys
import sqlite3
import datetime
from random import randint

connection = None
cursor = None

class Interface:

    def __init__(self):
        self.exit_app = False   # set to TRUE when user attempts to quit application
        self.logged_in = False  # set to TRUE when user has successfully logged in
        self.get_database()
        self.run()
    
    def get_database(self):
        self.database = input("Name of database: ")
    
    def run(self):
        while not self.exit_app:
            self.login()
            while self.logged_in:
                if self.user_type == 'a':
                    self.agent()
                elif self.user_type == 'o':
                    self.officer()
            print("You have been logged out.")
        print("You have exited the application.")
    
    def login(self):
        global connection, cursor
        while not self.exit_app and not self.logged_in:
            print("\nPlease insert valid username and password\n")
            username = input("Username: ")
            password = input("Password: ")
            
            connection = sqlite3.connect(self.database) # establish connection to database
            cursor = connection.cursor()
            
            login_query = '''   SELECT *
                                FROM users
                                WHERE uid=:user_field AND pwd=:pass_field;
                                '''

            cursor.execute(login_query, {"user_field":username, "pass_field":password})
            found = cursor.fetchone()   # find user in database
            if found:
                self.user_type = found[2]
                self.user_city = found[5]
                self.logged_in = True
            else:
                print("\nInvalid username and/or password\nPlease try again")
    
    def agent(self):
        print('1 - Register a birth',
              '2 - Register a marriage',
              '3 - Renew a vehicle registration',
              '4 - Process a bill of sale',
              '5 - Process a payment',
              '6 - Get a driver abstract',
              'X - Logout',
              'XX - Exit Application', sep='\n')
        selection = input("\nSelect an option from 1-6, X, XX: ")
        if selection == '1':
            self.register_birth()
        elif selection == '2':
            self.register_marriage()
        elif selection == '3':
            self.renew_registration()
        elif selection == '4':
            self.process_sale()
        elif selection == '5':
            self.process_payment()
        elif selection == '6':
            self.get_driver_abstract()
        elif selection == 'X':
            self.logged_in = False
        elif selection == "XX":
            self.logged_in = False
            self.exit_app = True
        else:
            print("\nInvalid Input\nPlease try again\n")
    
    def officer(self):
        print('1 - Issue a ticket',
              '2 - Find a car owner',
              'X - Logout',
              'XX - Exit Application', sep='\n')
        selection = input("\nSelect an option from 1-2, X, XX: ")
        if selection == '1':
            self.issue_ticket()
        elif selection == '2':
            self.find_owner()
        elif selection == 'X':
            self.logged_in = False
        elif selection == "XX":
            self.logged_in = False
            self.exit_app = True
        else:
            print("\nInvalid Input\nPlease try again\n")
    
    def register_birth(self):

        insert_birth_query = '''    INSERT INTO births values
                                    (:r_no, :f_name, :l_name, :r_date, :r_place, :g, :f_fname, :f_lname, :m_fname, :m_lname);
                                    '''

        insert_person_query = '''   INSERT INTO persons VALUES
                                    (:fname_field, :lname_field, :bdate_field, :bplace_field, :address_field, :phone_field);
                                    '''
        check_person_query = '''    SELECT * 
                                    FROM persons 
                                    WHERE fname=:fname_field COLLATE NOCASE AND lname=:lname_field COLLATE NOCASE;
                                    '''

        b_fname = input("Enter newborn's first name: ")
        b_lname = input("Enter newborn's last name: ")

        cursor.execute(check_person_query, {"fname_field":b_fname, "lname_field":b_lname})
        found = cursor.fetchall()

        while found:
            print("Record already exists. Please try again.")
            b_fname = input("Enter newborn's first name: ")
            b_lname = input("Enter newborn's last name: ")
            cursor.execute(check_person_query, {"fname_field":b_fname, "lname_field":b_lname})
            found = cursor.fetchall()

        gender = input("Enter newborn's gender (M/F): ")
        bir_date = input("Enter newborn's birth date (YYYY-MM-DD): ")
        bir_place = self.user_city
        m_fname = input("Enter mother's first name: ")
        m_lname = input("Enter mother's last name: ")
        f_fname = input("Enter father's first name: ")
        f_lname = input("Enter father's last name: ")

        reg_date = reg_date = str(datetime.date.today())

        while True:     # generate unique registration number
            reg_no = randint(0, sys.maxsize)
            cursor.execute("SELECT * FROM births where regno=?;", (reg_no,))
            found = cursor.fetchone()
            if not found:   # if registration number is unique
                break

        cursor.execute(check_person_query, {"fname_field":m_fname, "lname_field":m_lname})
        found = cursor.fetchall()

        if not found: # no person found matching 'Mother'
            print("Mother not found. Please provide the following information: \n")
            bdate = input("Birth Date: ")
            if bdate == "":
                bdate = "NULL"

            bplace = input("Birth Place: ")
            if bplace == "":
                bplace = "NULL"

            address = input("Address: ")
            if address == "":
                address = "NULL"

            phone = input("Contact Number: ")
            if phone == "":
                phone = "NULL"

            cursor.execute(insert_person_query, {"fname_field":m_fname, "lname_field":m_lname, "bdate_field":bdate, "bplace_field":bplace, "address_field":address, "phone_field":phone})
            connection.commit()

        cursor.execute("SELECT * FROM persons WHERE fname=:m_fname COLLATE NOCASE AND lname=:m_lname COLLATE NOCASE;", {'m_fname':m_fname,'m_lname':m_lname})
           
        found = cursor.fetchone()

        m_address = found[4]
        m_phone = found[5]

        cursor.execute(check_person_query, {"fname_field":f_fname, "lname_field":f_lname})
        found = cursor.fetchall()

        if not found: # no person found matching 'Father'
            print("Father not found. Please provide the following information: \n")
            bdate = input("Birth Date: ")
            if bdate == "":
                bdate = "NULL"

            bplace = input("Birth Place: ")
            if bplace == "":
                bplace = "NULL"

            address = input("Address: ")
            if address == "":
                address = "NULL"

            phone = input("Contact Number: ")
            if phone == "":
                phone = "NULL"

            cursor.execute(insert_person_query, {"fname_field":f_fname, "lname_field":f_lname, "bdate_field":bdate, "bplace_field":bplace, "address_field":address, "phone_field":phone})
            connection.commit()

        cursor.execute(insert_birth_query, {"r_no":reg_no, "f_name":b_fname, "l_name":b_lname, "r_date":reg_date, "r_place":bir_place,
                                            "g":gender, "f_fname": f_fname, "f_lname":f_lname, "m_fname": m_fname, "m_lname":m_lname})
        connection.commit()

        cursor.execute(insert_person_query, {"fname_field":b_fname, "lname_field":b_lname, "bdate_field":bir_date, "bplace_field":bir_place, "address_field":m_address, "phone_field":m_phone})
        connection.commit()

        print("Birth has been successfully recorded!\n")
    
    def register_marriage(self):

        p1_fname = input("Enter Partner 1 First Name: ")
        p1_lname = input("Enter Partner 1 Last Name: ")
        p2_fname = input("Enter Partner 2 First Name: ")
        p2_lname = input("Enter Partner 2 Last Name: ")

        while True:     # generate unique registration number
            reg_no = randint(0, sys.maxsize)
            cursor.execute("SELECT * FROM marriages where regno=?;", (reg_no,))
            found = cursor.fetchone()
            if not found:   # if registration number is unique
                break

        reg_date = str(datetime.date.today())

        reg_place =  self.user_city

        check_person_query = '''    SELECT * 
                                    FROM persons 
                                    WHERE fname=:fname_field COLLATE NOCASE AND lname=:lname_field COLLATE NOCASE;
                                    '''
        insert_person_query = '''   INSERT INTO persons VALUES
                                    (:fname_field, :lname_field, :bdate_field, :bplace_field, :address_field, :phone_field);
                                    '''
        insert_marriage_query = ''' INSERT INTO marriages VALUES
                                    (:reg_no_field, :reg_date_field, :reg_place_field, :p1_fname_field, :p1_lname_field, :p2_fname_field, :p2_lname_field);
                                    '''
        cursor.execute(check_person_query, {"fname_field":p1_fname, "lname_field":p1_lname})
        found = cursor.fetchall()

        if not found:   # no person found matching 'Partner 1'
            print("Partner 1 not found. Please provide the following information: \n")
            bdate = input("Birth Date: ")
            if bdate == "":
                bdate = "NULL"

            bplace = input("Birth Place: ")
            if bplace == "":
                bplace = "NULL"

            address = input("Address: ")
            if address == "":
                address = "NULL"

            phone = input("Contact Number: ")
            if phone == "":
                phone = "NULL"

            cursor.execute(insert_person_query, {"fname_field":p1_fname, "lname_field":p1_lname, "bdate_field":bdate, "bplace_field":bplace, "address_field":address, "phone_field":phone})
            connection.commit()

        cursor.execute(check_person_query, {"fname_field":p2_fname, "lname_field":p2_lname})
        found = cursor.fetchall()

        if not found:   # no person found matching 'Partner 2'
            print("Partner 2 not found. Please provide the following information: \n")
            bdate = input("Birth Date: ")
            if bdate == "":
                bdate = "NULL"

            bplace = input("Birth Place: ")
            if bplace == "":
                bplace = "NULL"

            address = input("Address: ")
            if address == "":
                address = "NULL"

            phone = input("Contact Number: ")
            if phone == "":
                phone = "NULL"

            cursor.execute(insert_person_query, {"fname_field":p2_fname, "lname_field":p2_lname, "bdate_field":bdate, "bplace_field":bplace, "address_field":address, "phone_field":phone})
            connection.commit()

        cursor.execute(insert_marriage_query,   {"reg_no_field":reg_no, "reg_date_field":reg_date, "reg_place_field":reg_place, 
                                                "p1_fname_field":p1_fname, "p1_lname_field":p1_lname, "p2_fname_field":p2_fname, "p2_lname_field":p2_lname})
        connection.commit()

        print("Marriage has been successfully recorded!\n")
    
    def renew_registration(self):
        reg_no = int(input("Enter registration number: "))

        cursor.execute("SELECT * FROM registrations WHERE regno=?;", (reg_no,))
        found = cursor.fetchone()

        while not found:
            print("Invalid registration number. Please try again.")
            reg_no = int(input("Enter registration number: "))
            cursor.execute("SELECT * FROM registrations WHERE regno=?;", (reg_no,))
            found = cursor.fetchone()
        
        curr_expiry = found[2]
        today = str(datetime.date.today())

        if (curr_expiry <= today):  # if registration has expired
            cursor.execute("UPDATE registrations SET expiry=date('now', '+1 year') WHERE regno=?", (reg_no,))
            connection.commit()
        else:
            cursor.execute("UPDATE registrations SET expiry=date(expiry, '+1 year') WHERE regno=?", (reg_no,))
            connection.commit()

        print("Registration has been renewed!\n")

    def process_sale(self):
        vehicle_id = int(input("Enter Vehicle Identification Number (VIN): "))
        cursor.execute("SELECT * FROM registrations WHERE vin=?;", (vehicle_id,))
        found = cursor.fetchone()

        while not found:
            print("Invalid VIN. Please try again.")
            vehicle_id = int(input("Enter Vehicle Identification Number (VIN): "))
            cursor.execute("SELECT * FROM registrations WHERE vin=?;", (vehicle_id,))
            found = cursor.fetchone()
        
        curr_owner_fname = input("Enter Current Owner's First Name: ")
        curr_owner_lname = input("Enter Current Owner's Last Name: ")
        new_owner_fname = input("Enter New Owner's First Name: ")
        new_owner_lname = input("Enter New Owner's Last Name: ")
        plate_no = input("Enter Plate Number: ")

        
        if found[5]!=curr_owner_fname or found[6]!=curr_owner_lname:
            print("Incorrect current owner. Please try again.")
            process_sale(self)

        reg_no = found[0]
        cursor.execute("UPDATE registrations SET expiry=date('now') WHERE regno=?;", (reg_no,)) # update current registration to expire today
        connection.commit()

        while True:     # generate unique registration number
            reg_no = randint(0, sys.maxsize)
            cursor.execute("SELECT * FROM registrations where regno=?;", (reg_no,))
            found = cursor.fetchone()
            if not found:   # if registration number is unique
                break
        
        insert_reg_query = '''  INSERT INTO registrations VALUES
                                (:reg_no_field, date('now'), date('now', '+1 year'), :plate_field, :vin_field, :fname_field, :lname_field);
                                '''
        cursor.execute(insert_reg_query, {"reg_no_field":reg_no, "plate_field":plate_no, "vin_field":vehicle_id, "fname_field":new_owner_fname, "lname_field":new_owner_lname})
        connection.commit()

        print("Sale has been processed!\n")


    def process_payment(self):
        ticket_no = int(input("Enter the ticket number: "))
        cursor.execute("SELECT * FROM tickets WHERE tno=?;", (ticket_no,))
        found = cursor.fetchone()

        # check for valid ticket number
        while not found:
            print("Invalid Ticket Number. Please try again.")
            ticket_no = int(input("Enter the ticket number: "))
            cursor.execute("SELECT * FROM tickets WHERE tno=?;", (ticket_no,))
            found = cursor.fetchone()

        fine = found[2]

        pay_date = str(datetime.date.today())

        # check for multiple payments in same day
        cursor.execute("SELECT * FROM payments WHERE tno=:ticket_no_field AND pdate=:date_field;", {"ticket_no_field":ticket_no, "date_field":pay_date})
        found = cursor.fetchone()
        if found:
            print("Cannot process multiple payments on same day. Please try again tomorrow.")
            sys.exit()

        insert_amt_query = '''  INSERT INTO payments
                                VALUES (:t_no, :t_date, :t_amt );
                                '''
                                
        while True:
            amt_paying = int(input("Please enter the payment amount: "))
            if amt_paying > fine:
                amt_paying = int(input("Error! Amount Remaining:{}.\n"))
            else:
                break
            
        cursor.execute("SELECT SUM(amount) FROM payments WHERE tno=:t_no GROUP BY tno;", {"t_no":ticket_no})
        found = cursor.fetchone()

        # if first payment
        if not found:
            print("Thank you! Amount Remaining:{}.\n".format(fine-amt_paying))
            cursor.execute(insert_amt_query, {"t_no":ticket_no,"t_date":pay_date,"t_amt":amt_paying})
            connection.commit()
        
        # if partial payment has been made before
        else:
            amt_paid = found[0]
            
            while (amt_paid + amt_paying > fine):
                print("Error! Amount Remaining:{}.\n".format(fine - amt_paid))
                amt_paying = int(input("Please enter the payment amount: "))

            sum_amt = amt_paid + amt_paying
            cursor.execute(insert_amt_query, {"t_no":ticket_no,"t_date":pay_date,"t_amt":amt_paying})
            connection.commit()
            if sum_amt < fine:
                print("Thank you! Amount Remaining:{}.\n".format(fine - sum_amt))
            elif sum_amt == fine:
                print("You have paid off your ticket.")
                

    def get_driver_abstract(self):
            
        p_fname = input("Driver's First name: ")
        p_lname = input("Driver's Last name: ")

        # finds the number of tickets
        cursor.execute("SELECT COUNT(*)\
                        FROM registrations r, tickets t\
                        WHERE r.fname = ? COLLATE NOCASE AND r.lname = ? COLLATE NOCASE\
                        AND r.regno = t.regno;", (p_fname, p_lname))
        found = cursor.fetchone()
        num_tickets = found[0] 

        # finds the number of demerit points
        cursor.execute("SELECT COUNT(*)\
                        FROM demeritNotices\
                        WHERE fname=:f_name COLLATE NOCASE AND lname=:l_name COLLATE NOCASE;", {"f_name":p_fname, "l_name":p_lname})
        found = cursor.fetchone()
        num_dmp = found[0]

        # finds the sum of demerit points of last 2years, if nothing found then sets to 0
        cursor.execute("SELECT SUM(points)\
                        FROM demeritNotices\
                        WHERE fname=:f_name COLLATE NOCASE AND lname=:l_name COLLATE NOCASE\
                        AND ddate = date('now','-2 years');", {"f_name":p_fname, "l_name":p_lname})
        found = cursor.fetchone()
        if not found :
            sum_dmp = 0
        dmp_2years = found[0]


        # finds the sum of demerit points of lifetime, if nothing found then sets sum to 0
        cursor.execute("SELECT SUM(points)\
                        FROM demeritNotices\
                        WHERE fname=:f_name COLLATE NOCASE AND lname=:l_name COLLATE NOCASE;", {"f_name":p_fname, "l_name":p_lname})
                        
        found = cursor.fetchone()
        if not found:
            dmp_lifetime = 0

        dmp_lifetime = found[0]

        print("Driver's Abstract\n")
        print ("Number of Tickets {} | Number of Demerit Notices {} | Demerit Points (Last 2 years) {} | Demerit Points (Lifetime) {}".format(num_tickets, num_dmp, dmp_2years, dmp_lifetime))

        check = input("Would you like to see the tickets associated with this driver (Y/N): ")

        if check == 'Y':
            cursor.execute("SELECT t.tno, t.vdate, t.violation, t.fine, r.regno, v.make, v.model\
                            FROM tickets AS t\
                            LEFT OUTER JOIN registrations AS r on t.regno = r.regno\
                            LEFT OUTER JOIN vehicles AS v on r.vin = v.vin\
                            WHERE r.fname =:f_name and r.lname =:l_name\
                            ORDER by t.vdate DESC;", {"f_name":p_fname, "l_name":p_lname})
            found = cursor.fetchall()

            first = 0 
            last = 5

            # less than 5 tickets
            if num_tickets <= 5:
                for t_no in range(first, last):
                    print(  "Ticket Number: {} | Violation Date:{} | Violation: {} | Amount: {} | Registration No.: {} | Make: {} | Model : {}"
                            .format(found[t_no][0], found[t_no][1], found[t_no][2], found[t_no][3], found[t_no][4], found[t_no][5], found[t_no][6]))
            # more than 5 tickets
            # display 5 at a time
            else:
                while True:
                    for t_no in range(first, last):
                        print(  "Ticket Number: {} | Violation Date:{} | Violation: {} | Amount: {} | Registration No.: {} | Make: {} | Model : {}"
                                .format(found[t_no][0], found[t_no][1], found[t_no][2], found[t_no][3], found[t_no][4], found[t_no][5], found[t_no][6]))

                    check_more = input("Would you like to see more tickets (Y/N): ")

                    if check_more == 'Y':                            
                        first = last
                        if (last + 5 < num_tickets):
                            last += 5
                        else:
                            last = num_tickets
                    else:
                        break
        elif check == 'N':
            sys.exit()
    
    def issue_ticket(self):
        reg_no = input("Please enter the registration number: ")

        cursor.execute("SELECT * FROM registrations where regno=:reg", {"reg":reg_no})
        found = cursor.fetchone()

        while not found:
            print("Invalid Registration Number. Please try again.")
            reg_no = input("Please enter the registration number: ")
            cursor.execute("SELECT * FROM registrations where regno=:reg", {"reg":reg_no})
            found = cursor.fetchone()

        search_registration_query = ''' SELECT r.fname, r.lname, v.make, v.model, v.year, v.color
                                        FROM vehicles as v, registrations as r
                                        WHERE r.regno=:reg_no_field
                                        AND r.vin = v.vin;
                                        '''
        cursor.execute(search_registration_query, {"reg_no_field":reg_no})
        found = cursor.fetchone()

        print(  "Driver Name: {} {} | Make : {} | Model : {} | Year : {} | Color : {}"
                .format(found[0], found[1], found[2], found[3], found[4], found[5]))

        v_date = input("Please enter the violation date (YYYY-MM-DD): ")
        if not v_date:
            v_date = str(datetime.date.today())

        v_text = input("Enter description: ")

        v_fine = int(input("Enter fine amount: "))

        while True:     # generate unique ticket number
            t_no = randint(0, sys.maxsize)
            cursor.execute("SELECT * FROM tickets where tno=?;", (t_no,))
            found = cursor.fetchone()
            if not found:   # if ticket number is unique
                break

        cursor.execute("INSERT INTO tickets VALUES (?,?,?,?,?)", (t_no, reg_no, v_fine, v_text, v_date))
        connection.commit()

        print("Ticket issued successfully!")
    
    def find_owner(self):

        make_input = input("Enter the make of the car: ")
        model_input = input("Enter the model of the car: ")
        year_input = input("Enter the model year of the car: ")
        color_input = input("Enter the color of the car: ")
        plate_input = input("Enter the plate number of the car: ")

        search_query = '''  SELECT v.make, v.model, v.year, v.color, r.plate, r.regdate, r.expiry, r.fname, r.lname
                            FROM registrations r, vehicles v
                            WHERE r.vin = v.vin'''

        # add to query if field has been provided
        if make_input != "":
            search_query += " AND v.make='{}'".format(make_input)
        if model_input != "":
            search_query += " AND v.model='{}'".format(model_input)
        if year_input != "":
            search_query += " AND v.year='{}'".format(year_input)
        if color_input != "":
            search_query += " AND v.color='{}'".format(color_input)
        if plate_input != "":
            search_query += " AND r.plate='{}'".format(plate_input)
        search_query += " COLLATE NOCASE;"

        cursor.execute(search_query)
        found = cursor.fetchall()
        matches = len(found)

        # if number of matches are more than 4
        if (matches > 4):
            for i in range(len(found)):
                print("{0} - {1} | {2} | {3} | {4} | {5}\n".format(i+1, found[i][0], found[i][1], found [i][2], found [i][3], found [i][4]))

            # allow user to select
            user_select = int(matches + 1)
            while (user_select > matches or user_select <= 0):
                user_select = int(input("Choose from 1 - {}: ".format(matches)))
                if (user_select > matches or user_select <= 0):
                    print("Invalid Input. Please try again.\n")

            index = user_select - 1
            print(  "Make: {0} | Model: {1} | Year: {2} | Color: {3} | Plate: {4} | Registration Date: {5} | Expiry Date: {6} | Owner Name: {7} {8}\n"
                    .format(found[index][0], found[index][1], found [index][2], found [index][3], found [index][4], found[index][5], found[index][6], found [index][7], found [index][8]))

        # if number of matches is between 1-4
        elif (matches > 0 and matches <= 4):
            for i in range(len(found)):
                print(  "Make: {0} | Model: {1} | Year: {2} | Color: {3} | Plate: {4} | Registration Date: {5} | Expiry Date: {6} | Owner Name: {7} {8}\n"
                        .format(found[i][0], found[i][1], found [i][2], found [i][3], found [i][4], found[i][5], found[i][6], found [i][7], found [i][8]))
        
        elif (matches == 0):
            print("No matches found.\n")
        
def main():
    Interface()

if __name__ == "__main__":
    main()