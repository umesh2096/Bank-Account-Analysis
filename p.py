'''
Created between 01-April-2017-----10-April-2017

@author: umesh
'''
import sys
import random
import re
import cx_Oracle
'''class for the sign up'''
class newCustomer:
    accountList=[];
    ct=0
    entry=1
    def inputDetail(self):
        try:
            self.entry=1
            self.fname=input("Enter the First Name: ");
            self.lname=input("Enter the Last Name: ");
            self.address=input("Enter the address: ")
            self.state=input("Enter the state: ");
            self.city=input("Enter the city: ");
            self.pincode=input("Enter the pincode: ");
            self.email=input("Enter the email address: ")
            self.mobileNo=input("Enter the Mobile No.");
            self.doc=input("Enter the current date(mm/dd/yyyy): ");
            self.accountType=input("Enter the account type(savings/current): ");
            self.balance=int(input("Enter the minimum balance to be deposited(Savings:0.00 Rs, Current: 5000 Rs): "));
            if(self.validateDetail()==0):
                print("\nRegistration Successful")
                self.accountIdGenerator()
                print("Your Account Number is ",self.accountNo)
                if self.ct<=3:
                    self.createPassword()
            else:
                print("\nRegistration Unsuccessful")
                self.entry=0
        except:
            print("\nInvalid Input")
        return
    
    def createPassword(self):
        try:
            self.password=input("Create your password: ")
            if(self.validatePassword()==0):
                print("\nPassword Created Successfully")
                print("Your Account has been Created successfully in the Bank. Please Use your Customer Id and password for Login")
                return
            else:
                self.ct=self.ct+1
                print("\nTry Again")
                if self.ct>=3:
                    print("\nSorry limit has been exceeded. Your Registration has been cancelled")
                    return
                else:
                    self.createPassword()
        except:
            print("\nInvalid Input")
            return
            
    def validatePassword(self):
        self.t=0
        if(re.match("\w{7,}", self.password)==None):
            print("Enter the correct password")
            print("\nIt should be minimum 8 characters and can be any combination of numeric and alphabets.")
            self.t=1
        return self.t;    
    
    def validateDetail(self):
        print("\n")
        self.free=0
        if(re.match("^\d{6}$",self.pincode)==None):
            print("Enter the correct pincode")
            self.free=1
        if(re.match("^\d{10}$",self.mobileNo)==None):
            print("Enter the correct Mobile No")
            self.free=1
        if(self.accountType!="savings" and self.accountType!="current"):
            print("Enter the correct account type")
            self.free=1 
        if((re.match("\D{1,20}",self.fname)==None) or (re.match("\D{1,20}",self.lname)==None)):
            print("Max 20 characters allowed in first name or last name")
            self.free=1 
        if((re.match("\w{1,40}",self.email)==None) or (re.match("\D{1,40}",self.state)==None) or (re.match("\D{1,40}",self.city)==None) or (re.match("\D{1,100}",self.address)==None)):
            print("Max characers limit exceeded in email/state/city/address")
            self.free=1
        if(self.accountType=="current"):
            if(self.balance<5000):
                print("Insufficient Balance. Minimum Balance of 5k Rs required to open current account ");
                self.free=1
        if(re.match("^(0[1-9]|1[1-2])[/](0[1-9]|1[0-9]|2[0-9]|3[0-1])[/](201[0-7])$",self.doc)==None):
            print("Invalid Date . Enter date between 2010 and 2017 in mm/dd/yyyy format")
            self.free=1
        if(self.balance<=0):
            print("Invalid amount. Please enter the correct amount")
            self.free=1
        return self.free;

    def accountIdGenerator(self):
        temp=random.randrange(3000000000,3999999999);
        while(temp in self.accountList):
            temp=random.randrange(3000000000,3999999999);
        self.accountNo=temp;
        self.accountList.append(self.accountNo);

    def storeDetail(self):
        try:
            temp2=self.password
            con=cx_Oracle.connect('PRO/samant@localhost/xe')
            cur=con.cursor()
            cur.execute("""insert into customer values(:1,:2,:3,:4,:5,:6,:7,to_date(:8,'MM/DD/YYYY'))""",(self.accountNo,self.fname,self.lname,self.email,self.mobileNo,self.accountType,self.balance,self.doc));
            cur.execute('insert into customerAddress values(:1,:2,:3,:4,:5)',(self.accountNo,self.address,self.state,self.city,self.pincode))
            cur.execute("""insert into login values(:1,:2,'active')""",(self.accountNo,temp2));
            con.commit();
            con.close();
        except:
            print("\nError Occurred")
            return

'''class for the sign in of existing customer. existingCustomer class inherits newCustomer class'''    
class existingCustomer(newCustomer):
    ctr=0       
    a=[]
    cnt=0
    t=1
    def validateLogin(self):
        try:
            con=cx_Oracle.connect('PRO/samant@localhost/xe')
            cur=con.cursor();    
            self.accnt=int(input("\nEnter your AccountNO:"))
            cur.execute("""select accountno from login where accountno= %d """%(self.accnt))
            self.accountL=cur.fetchall()
            if len(self.accountL)==0:
                print("\nUser Doesn't Exist")
                return
            else:
                self.passw=input("Enter your password")
                cur.execute("""select password from login where password= '%s' """%(self.passw))
                self.accountL=cur.fetchall()
                cur.execute("""select accountstatus from login where accountno= %d """%(self.accnt))
                self.status=str(cur.fetchall()[0][0])
                if self.status=='locked':
                    print("\nyour account has been locked due to exceeding limit of login attempts. Contact to the nearest branch")
                    return
                elif len(self.accountL)==0:
                    print("\npassword is invalid")
                    self.ctr=self.ctr+1;
                    print("\nInvalid customer_id or password. Please try Again.")
                    if(self.ctr==3):
                        cur.execute("""update login set accountstatus='locked' where accountno= %d """%(self.accnt))
                        print("Your Account has been locked due to exceeding limit of login attempts")
                        self.ctr=0;
                        con.commit();
                        return
                    else:
                        self.validateLogin()
                else:
                    print("\nLogged In successfully")
                    self.subMenu()
                    con.commit();
                    return
        except:
                print("\nError Occurred")
                return

    def subMenu(self):
        try:
            con=cx_Oracle.connect('PRO/samant@localhost/xe')
            cur=con.cursor()
            print("\n1.Address Change")
            print("2.Open New Account")
            print("3.Money Deposit")
            print("4.Money Withdrawal")
            print("5.Print Statement")
            print("6.Transfer Money")
            print("7.Account Closure")
            print("8.Avail Loan")
            print("0.Customer Logout")
            option=int(input("\nEnter your option: "))
            if option==1:
                self.addressChange(cur,con)
            elif option==2:
                print("\n2.1 Open New SA\n2.2 Open New CA\n2.3 Open New FD")
                subchoice=float(input("Enter your choice: "))
                if subchoice==2.1 or subchoice==2.2:
                    self.inputDetail()
                    self.storeDetail()
                elif subchoice==2.3:
                    fd_amt=int(input("Enter the amount to be deposited in FD: "))
                    fd_dur=int(input("Enter the duration in months: "))
                    if(fd_amt<1000) and ((fd_amt%1000)!=0):
                        print("\nInvalid amount. Please enter amount in multiples of 1000")
                    elif fd_dur<12:
                        print("\nInvalid duration. Please enter duration in valid no. of months")
                    else:
                        self.FdIdGenerator()
                        cur.execute("""insert into fdacc values(:1,:2,sysdate,:4,:5) """,{'1':self.fdid,'2':self.accnt,'4':fd_dur,'5':fd_amt})
                        print("Your FD no is ",self.fdid)
                        print("\n",fd_amt," is deposited for ",fd_dur," months")
                        con.commit()
                else:
                    print("\nInvalid option")
            elif option==3:
                self.moneyDeposit(cur,con)
            elif option==4:
                self.moneyWithdrawal(cur,con)
            elif option==5:
                self.miniStatement(cur,con)
            elif option==6:
                self.transferMoney(cur,con)
            elif option==7:
                self.accountClosure(cur,con)
                return
            elif option==8:
                self.availloan(cur,con)
            elif option==0:
                con.close()
                print("\nLogged out successfully")
                return
            else:
                print("\nInvalid input")
            self.subMenu()
        except:
            print("\nError Occurred")
            self.subMenu()
        
    def availloan(self,cur,con):
        try:
            loan_amnt=int(input("Enter the loan amount: "))
            loan_term=int(input("Enter the repayment term: "))
            cur.execute("""select balance from customer where accountno=:1""",{'1':self.accnt})
            bal=int((cur.fetchall()[0][0]))
            cur.execute("select accounttype from customer where accountno=:1""",{'1':self.accnt})
            accc=str((cur.fetchall()[0][0]))
            if accc=='current':
                print("This is current account . It cann't availed loan")
            elif loan_amnt<0 or ((loan_amnt%1000)!=0) or loan_term<=0:
                print("\nInvalid loan amount or repayment term.")
            elif (loan_amnt>(2*bal)):
                print("\nLoan process cann't be proceed due to insufficient balance in the account")
            else:
                self.loanIdGen()
                cur.execute("""insert into loan values(:1,:2,:3,:4)""",{'1':self.loanid,'2':self.accnt,'3':loan_amnt,'4':loan_term})
                con.commit()
                print("\n")
                print("LoanId\t\tAccountno\t\tAmount\t\tDuration\n")
                cur.execute(""" select *from loan where accountno=:1""",{'1':self.accnt})
                v=cur.fetchall()
                for i in v:
                    for j in i:
                        print(j,end="\t\t")
                    print("\n")
            return
        except:
            print("\nError occurred")
            return
    
    def loanIdGen(self):
        temp=random.randrange(10000,99999);
        while(temp in self.a):
            temp=random.randrange(10000,99999);
        self.loanid=temp;
        self.a.append(self.loanid);
            
    def FdIdGenerator(self):
        temp=random.randrange(10000,99999);
        while(temp in self.a):
            temp=random.randrange(10000,99999);
        self.fdid=temp;
        self.a.append(self.fdid);
    
    def addressChange(self,cur,con):
        try:
            self.addr=input("\nEnter the address: ")
            self.stt=input("Enter the state: ");
            self.cit=input("Enter the city: ");
            self.pin=input("Enter the pincode: ");
            if re.match("^\w{6}$",self.pin)!=None and re.match("^\w{40}",self.addr)!=None and re.match("^\w{40}",self.stt)!=None and re.match("^\w{40}",self.cit)!=None:
                cur.execute('update customerAddress set address=:a , state=:b , city=:c, pincode=:d where accountno=:e', {'a':self.addr,'b':self.stt,'c':self.cit,'d':self.pin,'e':self.accnt})
                con.commit();
                print("\nAddress updated successfully")
            else:
                print("\nUpdation Unsuccessful")
                return
        except:
            print("\nError Occurred")
            return
        
    def moneyDeposit(self,cur,con):
        try:
            bal=int(input("Enter the balance to be deposited: "));
            cur.execute('select balance from customer where accountNo=:1',(self.accnt,))
            temp_bal=int((cur.fetchall())[0][0])
            tot=temp_bal+bal;
            cur.execute('update customer set balance=:1 where accountno=:2',(tot,self.accnt))
            cur.execute("""insert into transactions values(:1,NULL,'cr',sysdate,:4,:5)""",{'1':self.accnt,'4':bal,'5':tot})
            print("\nAmount deposited successfully")
            print("Your Total Balance: ",tot)
            con.commit();
            return
        except:
            print("\nError Occurred")
            con.rollback()
            return
        
    def moneyWithdrawal(self,cur,con):        
        try:
            bal=int(input("\nEnter the balance to be withdrawal: "));
            cur.execute('select balance from customer where accountNo=:1',(self.accnt,))
            temp_bal=int((cur.fetchall())[0][0])
            cur.execute("""select accounttype from customer where accountNo=:1""",{'1':self.accnt})
            var=str((cur.fetchall())[0][0])
            tot=temp_bal-bal;
            if var=='current' and tot<=5000:
                print("\nWithdraw unsuccessful. Insufficient Balance")
            elif bal<0:
                print("\nInvalid amount")
            else:
                cur.execute('update customer set balance=:1 where accountno=:2',(tot,self.accnt))
                cur.execute("""insert into transactions values(:1,NULL,'dr',sysdate,:4,:5)""",{'1':self.accnt,'4':bal,'5':tot})
                print("\nAmount Withdrawal successfully")
                print("Your Total Balance: ",tot)
                con.commit()
        except Exception as e:
            print(e)
            con.rollback()
            return
    
    def transferMoney(self,cur,con):
        try:
            ben_acc=int(input("Enter the beneficiary account no : "))
            cur.execute("""select accountno from customer where accountno=%d """%(ben_acc))
            self.accountL=cur.fetchall()
            if len(self.accountL)==0:
                print("\nInvalid account no")
                return
            else: 
                ben_amt=int(input("Enter the amount to be transferred: "))
                cur.execute("""select balance from customer where accountNo=%d """%(self.accnt))
                paye_bal=int((cur.fetchall())[0][0])
                b=paye_bal-ben_amt;
                cur.execute("""select accounttype from customer where accountNo=:1""",{'1':self.accnt})
                var=str((cur.fetchall())[0][0])
                if var=='current' and b<=5000:
                    print("\nTransfer unsuccessful. Insufficient Balance")
                elif ben_amt<0:
                    print("\nInvalid amount")
                else:
                    cur.execute("""update customer set balance=:1 where accountNo=:2 """,(b,self.accnt))
                    cur.execute("""insert into transactions values(:1,:2,'dr',sysdate,:5,:6)""",{'1':self.accnt,'2':ben_acc,'5':ben_amt,'6':b})
                    print("\nAmount transferred successfully")
                    print("Your Total Balance: ",b)
                    cur.execute("""select balance from customer where accountNo=:1""",(ben_acc,));
                    ben_bal=int((cur.fetchall())[0][0])
                    b=ben_bal+ben_amt;
                    cur.execute('update customer set balance=:1 where accountNo=:2',(b,ben_acc))
                    cur.execute("""insert into transactions values(:1,:2,'cr',sysdate,:5,:6)""",{'1':ben_acc,'2':self.accnt,'5':ben_amt,'6':b})
                    con.commit()
                return
        except:
            print("\nError Occurred")
            con.rollback()
            return
        
    def miniStatement(self,cur,con):
        try:
            start_date=input("enter the starting date(mm/dd/yyyy): ")
            end_date=input("enter the end date(mm/dd/yyyy): ")
            new_strt=start_date+' 00:00:00'
            new_end=end_date+' 23:59:59'
            print(self.accnt)
            print("\n\n Self_AccountNo \t Ben_Accountno\t\tTransaction_Type\t\tDate_Of_Trans \t\t\t Transaction_Amount\t\t Remaining_Balance\n\n")
            cur.execute("""select *from transactions where (date_of_transaction between to_date(:1,'MM/DD/YYYY HH24:MI:SS') and to_date(:2,'MM/DD/YYYY HH24:MI:SS')) and (accountno=:3)""",(new_strt,new_end,self.accnt));
            var=cur.fetchall()
            if len(var)==0:
                print("\nTransactions are not available in this range")
            else:
                for i in var:
                    for j in i:
                        print(j,end="\t\t\t")
                    print("\n")
            con.commit()
            return
        except:
            print("\nError Occurred")
            return
        
    def accountClosure(self,cur,con):
        try:
            ch=input("\nAre you sure you want to close your account(press y for yes or press n for no:) ");
            if(ch=='y'):
                cur.execute('select balance from customer where accountNo=:1',(self.accnt,))
                t_bal=int((cur.fetchall())[0][0])
                cur.execute("""insert into closedAccount values(:1,sysdate)""",(self.accnt,))
                cur.execute('delete from customer where accountNo=:1',(self.accnt,))
                print("\nRemaining balance ",t_bal," Rs will be delivered to your address")
                print("Account deleted successfully")
                con.commit();
            return
        except:
            print("Error Occurred")
            return

'''class for the sign in of admin'''
class admin:
    def signIn(self):
        try:
            adminId=input("Enter the admin id: ")
            adminPas=input("Enter the password: ")
            try:
                con=cx_Oracle.connect(adminId,adminPas)
                print("\nLogged in Successfully")
                cur=con.cursor();    
                self.adminMenu(cur,con)
            except:
                print("\nInvalid Login Detail")
            return
        except:
            print("\nError Occurred")
            return
        
    def adminMenu(self,cur,con):
        try:
            print("\n")
            print("1.  Closed Accounts History")
            print("2.  FD Report of a Customer")
            print("3.  FD Report of Customer via-a-via another Customer")
            print("4.  FD Report w.r.t a particular FD amount");
            print("5.  Loan Report of a Customer")
            print("6.  Loan Report of Customer vis-a-vis another Customer")
            print("7.  Loan Report w.r.t a particular loan amount")
            print("8.  FD-Loan Report of a Customers")
            print("9.  Report of Customers who are yet to avail a loan")
            print("10. Report of Customers who are yet to open an FD account")
            print("11. Report of Customers who neither have a loan nor an FD account with the bank")
            print("0.  Admin Logout")
            opt=int(input("Enter the option: "))
            if opt==1:
                self.accountClosed(cur,con)
                self.adminMenu(cur, con)
            elif opt==2:
                des=int(input("\nEnter the account no of customer: "))
                cur.execute("""select accountno from customer where accountno=:1""",{'1':des})
                v=cur.fetchall()
                if len(v)==0:
                    print("\nInvalid Account no.")
                else:
                    print("\nAccountno\t  Name\t\t Amt \tTerm\tOpening_date\n")
                    cur.execute("""select c.accountno,c.fname,c.lname,f.deposit,f.duration,f.open_date from customer c inner join fdacc f on f.accountno=c.accountno where c.accountno=:1""",{'1':des})
                    va=cur.fetchall()
                    if len(va)!=0:
                        print("\n")
                        for i in va:
                            for j in i:
                                print(j,end="\t")
                            print("\n")
                    else:
                        print("\nN.A")
                self.adminMenu(cur, con)
                        
            elif opt==3:
                des=int(input("Enter the account no: "))
                cur.execute("""select accountno from fdacc where accountno=:1 """,{'1':des})
                v=cur.fetchall()
                print("\n\n")
                if len(v)!=0:
                    print("\nAccountno\tfdNo\tAmt\tTerm\n")
                    cur.execute("""select accountno,fdno,deposit,duration from fdacc group by fdno,accountno,deposit,duration having sum(deposit)>=(select sum(deposit) from fdacc where accountno=:1)""",{'1':des})
                    va=cur.fetchall()
                    if len(va)!=0:
                        for i in va:
                            for j in i:
                                print(j,end="\t")
                            print("\n")
                    else:
                        print("\nNo data Fetched")
                else:
                    print("\nInvalid Account no")
                self.adminMenu(cur, con)
            
            elif opt==4:
                cur.execute("select distinct(deposit) from fdacc");
                va=cur.fetchall()
                print("select particular amount from this list: ")
                l=[]
                for i in va:
                    for j in i:
                        l.append(j)
                        print(j)
                v=int(input("Enter the pariticular amount to see the FD Report: "))
                if v in l:
                    print("\nAccountno\t Name \t\tAmt\tOpen_date\n")
                    cur.execute("""select c.accountno,c.fname,c.lname,f.duration,f.open_date from customer c inner join fdacc f on f.accountno=c.accountno where f.deposit=:1 """,{'1':v})
                    s=cur.fetchall()
                    print("\n")
                    for i in s:
                        for j in i:
                            print(j,end="\t")
                        print("\n")
                else:
                    print("\nInvalid amount")
                self.adminMenu(cur, con)
        
            elif opt==5:
                des=int(input("Enter the account no of customer: "))
                cur.execute("""select accountno from customer where accountno=:1""",{'1':des})
                v=cur.fetchall()
                if len(v)==0:
                    print("\nInvalid Account no.")
                    self.adminMenu(cur, con)
                else:
                    print("\nAccountno\tName\t\tLoanId\tTerm\tAmnt\n")
                    cur.execute("""select c.accountno,c.fname,c.lname,l.loanid,l.duration,l.amount from customer c inner join loan l on l.accountno=c.accountno where l.accountno=:1""",{'1':des})
                    va=cur.fetchall()
                    if len(va)!=0:
                        print("\n")
                        for i in va:
                            for j in i:
                                print(j,end="\t")
                            print("\n")
                    else:
                        print("\nNot Availed")
                self.adminMenu(cur, con)
        
            elif opt==6:
                des=int(input("Enter the account no: "))
                cur.execute("""select accountno from loan where accountno=:1 """,{'1':des})
                v=cur.fetchall()
                print("\n\n")
                if len(v)!=0:
                    print("\nAccountno\tLoanId\tAmnt\tTerm\n")
                    cur.execute("""select accountno,loanid,amount,duration from loan group by loanid,accountno,amount,duration having sum(amount)>=(select sum(amount) from loan where accountno=:1)""",{'1':des})
                    va=cur.fetchall()
                    if len(va)!=0:
                        for i in va:
                            for j in i:
                                print(j,end="\t")
                            print("\n")
                    else:
                        print("\nNo data Fetched")
                else:
                    print("\nInvalid Account no")
                self.adminMenu(cur, con)
        
            elif opt==7:
                cur.execute("select distinct(amount) from loan");
                va=cur.fetchall()
                print("Select particular amount from this list: ")
                l=[]
                for i in va:
                    for j in i:
                        l.append(j)
                        print(j)
                v=int(input("Enter the pariticular amount to see the loan Report: "))
                if v in l:
                    print("\nAccountNo\tName\t\tAmnt")
                    cur.execute("""select c.accountno,c.fname,c.lname,l.amount from customer c inner join loan l on l.accountno=c.accountno where l.amount=:1 """,{'1':v})
                    s=cur.fetchall()
                    print("\n")
                    for i in s:
                        for j in i:
                            print(j,end="\t")
                        print("\n")
                    else:
                        print("\nInvalid amount")
                self.adminMenu(cur, con)
            
            elif opt==8:
                print("\n")
                print("Accountno\t\tfame\t\tlname\t\tsum_loan_amnt\tsum_fd_amnt\n")
                cur.execute("""select c.accountno,c.fname,c.lname,sum(f.deposit),sum(l.amount) from customer c ,fdacc f,loan l where c.accountno=f.accountno and l.accountno=c.accountno group by c.accountno,c.fname,c.lname having sum(l.amount) >=sum(f.deposit)""")
                va=cur.fetchall()
                if len(va)!=0:
                    for i in va:
                        for j in i:
                            print(j,end="\t\t")
                        print("\n")
                else:
                    print("\nNo data Fetched")
                self.adminMenu(cur, con)
                        
            elif opt==9:
                print("\n")
                print("Accountno\tName\n")
                cur.execute("""select accountno,fname,lname from customer where accountno not in (select l.accountno from customer c inner join loan l on l.accountno=c.accountno)""")
                va=cur.fetchall()
                if len(va)!=0:
                    for i in va:
                        for j in i:
                            print(j,end="\t")
                        print("\n")
                else:
                    print("\nNo data Fetched")
                self.adminMenu(cur, con)
            
            elif opt==10:
                print("\n")
                print("AccountNo\tName\n")
                cur.execute("""select accountno,fname,lname from customer where accountno not in (select f.accountno from customer c inner join fdacc f on f.accountno=c.accountno)""")
                va=cur.fetchall()
                if len(va)!=0:
                    for i in va:
                        for j in i:
                            print(j,end="\t")
                        print("\n")
                else:
                    print("\nNo data fetched")
                self.adminMenu(cur, con)
            
            elif opt==11:
                print("\nAccountNo\tName\n") 
                cur.execute("""select accountno,fname,lname from customer where accountno not in (select l.accountno from loan l inner join customer c on l.accountno=c.accountno union select f.accountno from fdacc f inner join customer c on f.accountno=c.accountno)""")
                va=cur.fetchall()
                if len(va)!=0:
                    for i in va:
                        for j in i:
                            print(j,end="\t")
                        print("\n")
                else:
                    print("\nNo data fetched")
                self.adminMenu(cur, con)
        
            elif opt==0:
                print("\nLogged Out Successfully")
                con.close()
                return
            else:
                print("\nInvalid Input")
            self.adminMenu(cur,con)
            return
        except Exception as e:
            print(e,"Error occurred")
            self.adminMenu(cur, con)
            return

    def accountClosed(self,cur,con):
        try:
            cur.execute('select *from closedAccount');
            var=cur.fetchall()
            if len(var)!=0:
                print("\n\n AccountNo \t \tDate_Of_Closing\n\n")
                for i in var:
                    for j in i:
                        print(j,end="\t\t")
                    print("\n")
            else:
                print("No data fetched")
                self.adminMenu(cur, con)
        except Exception as e:
            print(e)
            self.adminMenu(cur, con)
                
'''function for the main menu'''
def mainMenu():
    try:
        print("\n\n\tMain Menu\n");
        print("1.Sign Up(New Customer)");
        print("2.Sign In(Existing Customer)");
        print("3.Admin Sign in");
        print("4.Quit");
        choice=int(input("\n\nChoose the Option: "));
        c1=newCustomer();
        c2=existingCustomer();
        c3=admin();
        if choice==1:
            c1.inputDetail();
            if c1.ct<3 and c1.entry==1:
                c1.storeDetail();
            else:
                c1.ct=0
        elif choice==2:
            c2.validateLogin();
        elif choice==3:
            c3.signIn()
        elif choice==4:
            sys.exit(0)
        else:
            print("\nInvalid Input")
        mainMenu()
    except Exception as e:
        print(e)
        mainMenu()


mainMenu();
