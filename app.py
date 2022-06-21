
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from helpers import apology, login_required, Isstaff, month_num, validate_password
from sql_extract import SQL
import functions
from datetime import datetime
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use lib_man.db database
db = SQL('lib_mn.db')



def isadmin():
    ids = db.execute('SELECT user_id FROM staff')
    staff_id = [value['user_id'] for value in ids]
    return staff_id


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow users to change password"""

    #Check if the user is an admin or member

    if Isstaff(db,session["user_id"]):
        rpath = '/display/admin'
    else:
        rpath = '/display/member'

    if request.method == "POST":
        if not request.form.get('current_password'):
            return apology('Need to enter the current password',path =rpath)
        if not request.form.get('new_password'):
            return apology('Need to enter the new password', path =rpath)
        if not request.form.get('confirmation'):
            return apology('Reenter the new password', path =rpath)
        if request.form.get('new_password')!=request.form.get('confirmation'):
            return apology('Passwords are not matching', path = rpath)
        error = validate_password(request.form.get('new_password'))
        if error:
            return apology(error, path = rpath)

        new_password =request.form.get('new_password')

        #Insert password into the database
        db.execute("UPDATE user SET password=? WHERE id= ?",(new_password,session["user_id"]))

        return redirect(rpath)
    else:
        return render_template("change_password.html")

@app.route("/",methods=["GET", "POST"])
def index():
    return render_template('login.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username").strip(" ")
        password = request.form.get("password").strip(" ")
        if not username:
            return apology("must provide username", path = "/")

        # Ensure password was submitted
        if not password:
            return apology("must provide password", path = "/")

        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE username = ?", (username,))
        # Ensure username exists and password is correct
        if len(rows) != 1 or rows[0]["password"]!= password:
            return apology("invalid username and/or password", path = "/")


        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        '''
        Redirect to the appropriate page depending on whether the logged in
        person is an admin or member
        '''
        staff_usernames=db.execute('SELECT username from staff')
        staff_usernames = [x['username'] for x in staff_usernames]
        if request.form.get("username") in staff_usernames:
                 return redirect("/display/admin")
        return redirect("/display/member")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/display/<page>", methods=["GET", "POST"])
@login_required
def display_page(page):
    if page == "admin":
        return render_template("admin.html")
    if page == "member":
        return render_template("member.html")


@app.route("/hold_book", methods=["GET", "POST"])
@login_required
def hold_book():
        ISBN = request.form.get('ISBN').strip(" ")
        if not ISBN:
            return apology("Please provide the ISBN to hold a book",path = "/display/member")
        #Calling the hold_book functions which returns the new issue id and copy_id
        result = functions.hold_book(ISBN,session["user_id"],db)
        if isinstance(result,str):
            return apology(result,path = "/display/member")
        return render_template("hold_book_success.html",result= result)

@app.route("/checkout", methods=["GET","POST"])
@login_required
def checkout():
   if request.method=="POST":
     issue_id = request.form.get("issue_id").strip(" ")
     ISBN = request.form.get("ISBN").strip(" ")
     copy_id = request.form.get("copy_id").strip(" ")
     if not issue_id :
        return apology("Enter the issue_id", path = "/checkout")
     if not ISBN :
        return apology("Enter the ISBN" , path = "/checkout")
     if not copy_id:
        return apology("Enter the copyid" , path = "/checkout")

     status = functions.checkout_book(ISBN, issue_id, copy_id, session["user_id"], db)
     if isinstance(status,str):
        return apology(status, path = "/display/member")
     return render_template("checkout_success.html")
   else:
    return render_template("checkout.html")

@app.route("/future_req", methods=["GET", "POST"])
@login_required
def future_req():
    if request.method == "POST":
        #Read the ISBN for the book
        ISBN = request.form.get('ISBN')
        if not ISBN:
            return apology("Input the ISBN", path = "/future_req")

        result = functions.future_hold(db,ISBN,session["user_id"])

        if isinstance(result,str):
            return apology(result,path = "/display/member" )
        return render_template("future_hold_success.html")
    else:
        return render_template("future_req.html")

@app.route("/extend_req", methods=["GET", "POST"])
@login_required
def extend_req():
    if request.method == "POST":
        issue_id = request.form.get('issue_id')
        if not issue_id:
            return apology("You must input ssue_id" , path = '/extend_req')
        extend_result = functions.extend_book(db, int(issue_id), session["user_id"])
        if isinstance(extend_result,str):
            return apology(extend_result, path = "/display/member")
        return render_template('extension_success.html',result=extend_result)

    else:
        return render_template('extend_req.html')

@app.route("/ret_book", methods=["GET", "POST"])
@login_required
def ret_book():
    '''
    Only inputting the issue id to return
    '''
    if request.method == "POST":
        issue_id = request.form.get('issue_id')
        copy_id = request.form.get('copy_id')
        ISBN = request.form.get('ISBN')
        Isdamaged = request.form.get('Isdamaged')

        if not issue_id:
            return apology("You must input issue_id" , path = "/ret_book")
        if not copy_id:
            return apology("You must input the copy_id" , path = "/ret_book")
        if not ISBN:
            return apology("You must input the ISBN" , path = "/ret_book")
        if not Isdamaged:
            return apology("You must input status of the book" , path = "/ret_book")
        result = functions.return_book(db, issue_id, ISBN, copy_id, session["user_id"], int(Isdamaged))
        if isinstance(result,str):
            return apology(result,path = "/display/member")

        return render_template('ret_book_success.html')
    else:
        return render_template('ret_book.html')

@app.route("/summary", methods=["GET", "POST"])
@login_required
def summary():
    return render_template('user_summary.html')

@app.route("/user_summary/<option>", methods=["GET"])
@login_required
def user_summary_option(option):
    if option == "on_hold":
        on_hold= functions.user_summary(db,session["user_id"],option)
        #If there are no books on hold
        if not len(on_hold):
            return apology('No books on hold currently', path ='/summary')
        return render_template('hold_summary.html',on_hold=on_hold)
    if option == "checked_out":
        checked_out = functions.user_summary(db,session["user_id"],'checked_out')
        if not len(checked_out):
            return apology('No books checked out' , path = "/summary")
        return render_template('checkout_summary.html',checked_out=checked_out)
    if option == "fut_hold":
        fut_hold = functions.user_summary(db,session["user_id"],'fut_hold')
        if not len(fut_hold):
            return apology('No books on future hold' , path = "/summary")
        return render_template('futhold_summary.html',fut_hold=fut_hold)
    if option == "penality":
         penality = db.execute('SELECT Penlity FROM lib_members WHERE user_id=?',(session['user_id'],))[0]['Penlity']
         return render_template('penality.html',penality =[penality])


@app.route("/search_book", methods=["GET", "POST"])
@login_required
def search_book():

    if request.method == "POST":
        if request.form.get('ISBN'):
            value = {'ISBN':request.form.get('ISBN').strip(" ")}
        elif request.form.get('title'):
            value = {'Title':request.form.get('title').strip(" ")}
        elif request.form.get('author'):
            value = {'Author':request.form.get('author').strip(" ")}
        else:
            return apology("Need to input atleast one field",path = "/search_book")

        rows = functions.search_book(value,db)
        if isinstance(rows,str):
            return apology(rows, path = "/display/member")
        return render_template("hold_request.html",values=rows)

    else:
     return render_template("search_book.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method=='POST':
        username=request.form.get('username').strip(" ")
        name=request.form.get('name').strip(" ")
        DOB=request.form.get('DOB').strip(" ")
        email=request.form.get('email').strip(" ")
        gender=request.form.get('gender').strip(" ")
        isfaculty=int(request.form.get('type')=="Faculty")
        password=request.form.get('password').strip(" ")
        confirmation=request.form.get('confirmation').strip(" ")
        dept=request.form.get('department').strip(" ")

        if not username:
            return apology('Must provide a username', path = "/register")
        if not name:
            return apology('Must provide a name', path = "/register" )
        if not email:
            return apology('Must provide an email', path = "/register")
        if not gender:
            return apology('Must provide a gender', path = "/register")
        if not password:
            return apology('Must provide password', path = "/register")
        if not confirmation:
            return apology('Must provide confirmation', path = "/register")
        if password != confirmation:
            return apology('Passwords do not match', path = "/register")
        #To validate the password
        error = validate_password(password)
        if error:
                return error
        Flask("Logged in")
        try:
            rows = db.execute("INSERT INTO user(username,password) VALUES(?,?)",(username,password))
        except:
            return apology("Username already taken",path = "/register")
        session["user_id"]=rows
        db.execute('''INSERT INTO lib_members(user_id,Name,DOB,Email,Gender,Isfaculty,Dept)
                    VALUES(?,?,?,?,?,?,?)''',(session["user_id"],name,DOB,email,gender,isfaculty,dept))

        return redirect("/display/member")
    else:
        return render_template("register.html")


@app.route("/damagbook", methods=["POST","GET"])
@login_required
def damagbook():
    if request.method=="POST":
        subname = request.form.get('Subname')
        month = request.form.get('month')
        val_mn = str(datetime.strptime(month,'%B').month)
        #Check for number of damaged records subjectwise


        dam_records = db.execute('''SELECT COUNT(Isdamaged) AS total,Title,bc.ISBN  FROM book_copy bc
                                    INNER JOIN
                                        (SELECT NT.ISBN,copy_id,Title FROM
                                            (SELECT DISTINCT issue.ISBN,copy_id FROM issue
                                             WHERE ltrim(strftime('%m',Issuedate),"0") = ?) AS NT
                                         INNER JOIN book b
                                         ON NT.ISBN = b.ISBN
                                         WHERE b.Subname = ?) OT
                                    ON OT.ISBN = bc.ISBN AND OT.copy_id = bc.copy_id
                                    AND Isdamaged=1 GROUP BY bc.ISBN;''',(val_mn,subname,))

        if not len(dam_records):
            return apology('No damaged books', path = "/display/admin")
        return render_template('damgbook_summary.html',month=month,sub_name=subname,values=dam_records)
    else:
        sub = db.execute('''SELECT DISTINCT(Subname) FROM book''')
        month = db.execute('''SELECT DISTINCT(strftime('%m',Issuedate)) AS month
                          FROM issue''' )
        for iter in month:
            iter['month'] = datetime.strptime(iter['month'].lstrip('0'),"%m").strftime('%B')
        return render_template('damgbook_input.html',subs=sub,months=month)




@app.route("/debarstud",methods=["GET"])
@login_required
def debarstud():
    #Select the debarred students name
    stud = db.execute('''SELECT Name,username FROM lib_members lm
                         INNER JOIN user u
                         ON lm.user_id = u.id
                         WHERE Isdebarred=1 ''')
    if not len(stud):
        return apology('No debarred students', path = "/display/admin")
    return render_template('debarstud_summary.html',values=stud)

@app.route("/frequser",methods=["GET","POST"])
@login_required
def frequser():
    if request.method == "POST":
        month = request.form.get('month1')
        month_val = month_num(month)
        pop_users = db.execute('''SELECT Name,username,COUNT(i.issue_id) AS freq FROM lib_members lm
                     INNER JOIN issue i
                     ON lm.user_id = i.user_id
                     INNER JOIN user u
                     ON u.id = i.user_id
                     WHERE ltrim(strftime('%m',i.Issuedate),"0") =?
                     GROUP BY u.id
                     ORDER BY freq DESC,Name ASC LIMIT 3''',(month_val,))

        return render_template("pop_users.html",values1 = pop_users)

    else:
        #Send the valid months into the form
        valid_months = db.execute('''SELECT DISTINCT(strftime('%m',Issuedate)) AS month
                          FROM issue''' )
        for iter in valid_months:
            iter['month'] = datetime.strptime(iter['month'].lstrip('0'),"%m").strftime('%B')
        return render_template('frequser_input.html',values=valid_months)


@app.route("/popbooks",methods=["GET","POST"])
@login_required
def popbooks():
    if request.method == "POST":
        month = request.form.get('month')
        month_val = month_num(month)
        pop_books = db.execute('''SELECT b.ISBN,Title,COUNT(issue_id) AS total FROM book b
                      INNER JOIN issue i
                      ON b.ISBN = i.ISBN
                      WHERE ltrim(strftime('%m',i.Issuedate),"0") =?
                      GROUP BY b.ISBN
                      ORDER BY total DESC,Title ASC LIMIT 3''',(month_val,))
        return render_template('popbooks_summary.html', values = pop_books)

    else:
        #Send the valid months into the form
        valid_months = db.execute('''SELECT DISTINCT(strftime('%m',Issuedate)) AS month
                          FROM issue''')
        for iter in valid_months:
            iter['month'] = datetime.strptime(iter['month'].lstrip('0'),"%m").strftime('%B')
        return render_template('popbooks_input.html', months = valid_months)

@app.route("/overdue",methods=["GET"])
@login_required
def overdue():
    today = datetime.today().strftime('%Y-%m-%d')
    over_due_members = db.execute('''SELECT Name,username,
                                     JULIANDAY(?) - JULIANDAY(i.Returndate) AS days
                                     FROM lib_members lb
                                     INNER JOIN issue i
                                     ON lb.user_id = i.user_id
                                     INNER JOIN book_copy bc
                                     ON i.ISBN = bc.ISBN
                                     INNER JOIN user u
                                     ON i.user_id = u.id
                                     WHERE i.copy_id = bc.copy_id AND i.Returndate <=?
                                     AND bc.Ischecked=1''',(today,today,))

    if not len(over_due_members):
        return apology('No overdue members', path = "/display/admin")
    return render_template('overdue_summary.html',values = over_due_members)

