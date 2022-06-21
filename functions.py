from datetime import datetime,timedelta



def search_book(input_dict:dict,db):
    key = next(iter(input_dict))

    #Check if the input value is valid
    if input_dict[key] not in valid(key,db):
        return(f'Invalid value for {key}')

    if key == 'ISBN':
        isbn = input_dict[key]
        query= '''SELECT b.ISBN,Title,COUNT(bc.copy_id) AS bc_count
        FROM book b
		INNER JOIN book_copy  bc
		ON b.ISBN= bc.ISBN
        WHERE b.ISBN=? AND bc.Ischecked=0 AND bc.Isonhold=0 AND bc.Isdamaged=0
            GROUP BY b.ISBN
            HAVING bc_count>0'''
        value = (isbn,)

    elif key == 'Title':
        title = input_dict[key]
        query= '''SELECT b.ISBN,Title,COUNT(bc.copy_id) AS bc_count
        FROM book b
		INNER JOIN book_copy  bc
		ON b.ISBN= bc.ISBN
        WHERE b.ISBN=? AND bc.Ischecked=0 AND bc.Isonhold=0 AND bc.Isdamaged=0
            GROUP BY b.ISBN
            HAVING bc_count>0'''
        value = (title,)
    elif key == 'Author':
        author = input_dict[key]
        query= '''SELECT b.ISBN,Title,COUNT(bc.copy_id) AS bc_count
        FROM book b
		INNER JOIN book_copy  bc
		ON b.ISBN= bc.ISBN
        INNER JOIN author a
        ON bc.ISBN=a.ISBN
        WHERE a.author=? AND bc.Ischecked=0 AND bc.Isonhold=0 AND bc.Isdamaged=0
        GROUP BY b.ISBN
        HAVING bc_count>0'''
        value = (author,)

    rows = db.execute(query,value)

    if len(rows):
            return rows
    return("No copies of the book are currently available.Try for a future hold on the copies")

def valid(value,db):
    if value == 'ISBN' or value=='Title':
        result = db.execute(f'SELECT {value} FROM book')
    elif value == 'Author':
        result = db.execute('SELECT Author FROM author')
    l = [key[value] for key in result]
    return l


def hold_book(ISBN,user_id,db):

    # Check if the ISBN is valid
    if ISBN not in valid('ISBN',db):
        return('Incorrect ISBN')

    out = db.execute('''SELECT MAX(issue_id),NT.copy_id FROM
                        (SELECT issue_id,i.ISBN,i.copy_id FROM issue i
                         INNER JOIN book_copy bc
                         ON i.ISBN = bc.ISBN
                         WHERE i.copy_id = bc.copy_id AND
                         (Isonhold=1 OR Ischecked=1)AND user_id=?
                         AND i.ISBN=?) AS NT''',(user_id,ISBN))


    #Check if the last entry for the ISBN,copy_id combination which is active is already
    #checked out or on hold.
    if not all(value == None for value in out[0].values()):
        return ("You cannot hold/checkout more than one copy of a book")



    #Picks the min copy_id of the ISBN which is free, not_damaged,not_reserved,not on_hold
    #Creates a new issue id and gives the issue id to the user

    #return date and given date both are set to today
    date = datetime.today().strftime('%Y-%m-%d')

    min_copy_id = '''SELECT min(copy_id) AS copy_id
                FROM book_copy bc
                INNER JOIN book b
                ON bc.ISBN = b.ISBN
                WHERE b.ISBN=? AND bc.Ischecked=0 AND bc.isonhold=0 AND bc.Isdamaged=0'''


    min_cpy = db.execute(min_copy_id,(ISBN,))[0]['copy_id']

    #Selects the max issue_id currently present and generates the next id for the user

    max_issue = 'SELECT max(issue_id) AS issue_id FROM issue'
    mx_issue = db.execute(max_issue)
    value =int(0 if mx_issue[0]["issue_id"] is None else mx_issue[0]["issue_id"])

    new_issue_id = value + 1

    #Insert the issue_id,copy_id for the user into the table

    db.execute('''INSERT INTO issue(user_id,issue_id,ISBN,copy_id,Issuedate,Returndate)
                  VALUES
                  (?,?,?,?,?,?)''',(user_id,new_issue_id,ISBN,min_cpy,date,date))

    #Make Ishold in the book_copy table for the particular copy_id and ISBN

    db.execute('UPDATE book_copy SET Isonhold=1 WHERE ISBN=? AND copy_id=?',(ISBN,min_cpy,))

    # Return the new issue_id to the user

    return [{'issue_id':new_issue_id,'ISBN':ISBN,'copy_id':min_cpy}]

def checkout_book(ISBN,issue_id,copy_id,user_id,db):

    #Find last entry for the particular ISBN and copy_id combination
    out = db.execute('''SELECT MAX(issue_id) AS valid_id, Ischecked, Isonhold, user_id FROM issue i
                        INNER JOIN book_copy bc
                        ON i.ISBN = bc.ISBN
                        WHERE i.copy_id = bc.copy_id AND
                        i.copy_id = ? AND i.ISBN=?''',(copy_id,ISBN))



    # Check if the issue_id matches the one input by the user
    if out[0]['valid_id'] == int(issue_id):
        # Check if it is assigned to the particular user
        if out[0]['user_id'] == user_id:
        #Check if the copy is not checked out and not on hold
            if not out[0]['Ischecked'] and not out[0]['Isonhold']:
                return("The copy is returned.Place a hold again")
            if not out[0]['Ischecked']:
                #Update the issue and book_copy tables
                issuedate = datetime.today()
                returndate = issuedate + timedelta(days=14)



                db.execute('''UPDATE book_copy SET Ischecked=1, Isonhold=0
                    WHERE ISBN=? AND copy_id=?''',(ISBN,copy_id,))

                db.execute('''UPDATE issue SET Issuedate=?,Returndate=?
                    WHERE issue_id=?''',(issuedate.strftime('%Y-%m-%d'),returndate.strftime('%Y-%m-%d'),issue_id))
                return True
            else:
                return('The copy is already checked out')
        else:
            return("The issue _id is not assigned to you.You cannot do anything")

    else:
        return("Issue id doesn't match")




def future_hold(db,ISBN,user_id):

    #Check if the ISBN is valid
    if ISBN not in valid_ISBN(db):
        return('The ISBN is not valid')

    #Extract the available copies from the book_copy table
    available_copies = db.execute('''SELECT COUNT(copy_id) AS available FROM book_copy AS bc
                                    WHERE bc.ISBN=? AND Isonhold=0 AND Isdamaged=0 AND Ischecked=0
                                 ''',(ISBN,) )[0]['available']

    #If there are no available copies
    if available_copies==0:
        #Check the number of copies which are not on hold
        nonhold_copies = db.execute('''SELECT COUNT(copy_id) AS total FROM book_copy
                      WHERE ISBN=? AND Isonhold=0''',(ISBN,))[0]['total']
        #If there are copies not on hold
        if nonhold_copies:
            date_tday = datetime.today().strftime('%Y-%m-%d')
            #Select min return date for the first available copy
            min_return_date = db.execute('''SELECT MIN(Returndate) AS ret_date FROM
                                            (SELECT i.copy_id,Returndate FROM
                                            issue i
                                            INNER JOIN book_copy bc
                                            ON i.ISBN = bc.ISBN
                                            WHERE Isdamaged=0 AND
                                            bc.Ischecked=1
                                            AND i.copy_id = bc.copy_id
                                            AND Returndate > ? AND i.ISBN = ?) AS NT''',(date_tday,ISBN))[0]["ret_date"]


            #Check if there are any damaged or reserved books
            if min_return_date:
                avail_date = min_return_date
                #Check for available copies without a furture requester with return date greater than or equal to the min_return_date
                copy_avail = db.execute('''SELECT MIN(i.copy_id) AS copy_avail FROM book_copy bc
                                        INNER JOIN book b
                                        ON bc.ISBN = b.ISBN
                                        INNER JOIN issue i
                                        ON b.ISBN = i.ISBN
                                        WHERE bc.ISBN=? AND Ischecked=1
                                        AND Isdamaged = 0 AND bc.copy_id = i.copy_id  AND Returndate >= ?  AND Fut_req IS NULL''',(ISBN,avail_date,))[0]['copy_avail']


                if copy_avail:
                    copy_id = copy_avail
                    #Extract the username from the user table
                    username = db.execute('SELECT username FROM user WHERE id=?',(user_id,))[0]["username"]
                    # Update the book_copy for the particular ISBN and copy_id
                    db.execute('''UPDATE book_copy SET Fut_req =?
                                WHERE ISBN = ? AND copy_id = ?''',(username,ISBN,copy_id,))
                    return True

                else:
                    return("There is already a future requester for this book")
            else:
                 return("The books might be damaged,reserved or have not been returned yet")
        else:
            return("All the copies are currently on hold.Return time is undetermined")

    else:
        return("There are available copies right now,directly place a hold request for them")


def extend_book(db,issue_id,user_id):

    #Select ISBN and copy_id for the issue_id given
    det = db.execute('SELECT copy_id,ISBN FROM issue WHERE issue_id=?',(issue_id,))
    #Pick the maximum issue_id for the ISBN,copy_id combination
    user_det = db.execute('''SELECT MAX(issue_id) AS issue_id,user_id FROM issue
                             WHERE ISBN = ? AND copy_id = ?''',(det[0]['ISBN'],det[0]['copy_id']))
    #Check if the user_id matches
    if user_det[0]['issue_id'] == issue_id:
        #Check if the issue_id matches
        if user_det[0]['user_id'] == user_id:
            #Check if the book has been checked out by the user
            out = db.execute('''SELECT Fut_req,Numext,Issuedate,Returndate,Extendate FROM book_copy bc
                        INNER JOIN issue i
                        ON i.ISBN = bc.ISBN
                        WHERE i.issue_id=? AND bc.copy_id=i.copy_id AND Ischecked=1''',(issue_id,))
            if not len(out):
                return("The book is either on hold or returned.Check the hold summary for further details")
            # Check if the return date is surpassed

            old_retdate = out[0]["Returndate"]
            extendate = datetime.today()
            if datetime.strptime(old_retdate,'%Y-%m-%d') < extendate:
                return ('''You cannot extend the book as the return date for the book is breached.Return
                        the book to avoid further penality''')

            Old_extendate = out[0]['Extendate']
            Fut_Req = out[0]["Fut_req"]
            Num_ext = int(out[0]["Numext"])
            Issuedate = out[0]["Issuedate"]
            Isfaculty = db.execute('''SELECT Isfaculty FROM lib_members
                                        WHERE user_id=?''',(user_id,))[0]['Isfaculty']



            if not Fut_Req:
                if not Isfaculty:
                    if Num_ext<2:
                        returndate = datetime.today()+timedelta(days=14)
                        allow_exten = datetime.strptime(Issuedate,'%Y-%m-%d') + timedelta(days=28)
                    else:
                        return("The limit for maximum extension for the book is reached")

                else:
                        if Num_ext<5:
                            returndate = datetime.today()+timedelta(days=28)
                            allow_exten = datetime.strptime(Issuedate,'%Y-%m-%d') + timedelta(days=50)

                        else:
                            return("The limit for maximum extension for the book is reached")

            else:
                return("The book has been requested by a user")
        else:
            return ("This user id doesnt belong to you")
    else:
        return("Incorrect issue_id")

    #Update the table with the newreturn date and extension date

    if returndate > allow_exten:
            returndate = allow_exten
    Num_ext+=1
    returndate = returndate.strftime('%Y-%m-%d')
    extendate = extendate.strftime('%Y-%m-%d')
    db.execute('''UPDATE issue SET Returndate = ?, Extendate=?,Numext=?
                  WHERE issue_id = ?''',(returndate,extendate,Num_ext,issue_id,))
    return [{"issue_date":Issuedate,"old_extdate":Old_extendate,"ext_date":extendate,"old_retdate":old_retdate,"ret_date":returndate}]




def return_book(db,issue_id,ISBN,copy_id,user_id,Isdamaged):


   # Check if the issue belongs to the user
    out = db.execute('''SELECT MAX(issue_id) AS valid_id, Ischecked, Isonhold, user_id FROM issue i
                        INNER JOIN book_copy bc
                        ON i.ISBN = bc.ISBN
                        WHERE i.copy_id = bc.copy_id AND
                        i.copy_id = ? AND i.ISBN=?''',(copy_id,ISBN))


    user_det = db.execute('SELECT user_id,ISBN FROM issue WHERE issue_id=?',(issue_id,))

    # Check if the issue_id matches the one input by the user
    if out[0]['valid_id'] == int(issue_id):
         if user_det[0]['user_id'] == user_id:
            if not out[0]['Isonhold'] and not out[0]['Ischecked']:
                return("Book already returned")
            #if the book is checked out
            if out[0]['Ischecked']:
                    #Check if there is a delay in returning
                    return_date = db.execute('''SELECT Returndate FROM issue
                                WHERE issue_id = ?''',(issue_id,))[0]['Returndate']
                    delay = (datetime.today() - datetime.strptime(return_date,'%Y-%m-%d')).days

                    if delay > 0:
                        #Extract the original penality and update the penality
                        orig_penality = db.execute('SELECT Penlity FROM lib_members WHERE user_id=?',(user_id,))[0]["Penlity"]
                        new_penality = orig_penality+delay*5
                        db.execute('UPDATE lib_members SET Penlity=? WHERE user_id=?',(new_penality,user_id))
                        #If the Penlity is greater than 100, debar the student/faculty
                        if new_penality > 100:
                            db.execute('UPDATE lib_members SET Isdebarred=1 WHERE user_id=?',(user_id))


                    if Isdamaged:
                        db.execute('''UPDATE book_copy SET
                                    Isdamaged=1
                                    WHERE copy_id=? AND ISBN=?''',(copy_id,ISBN))

                    #Update the book_copy fields
                    db.execute('''UPDATE book_copy SET Ischecked=0
                                WHERE ISBN =? AND copy_id=?''',(ISBN,copy_id))
                    return True
            else:
                return("You have not checked out the book.The book is still on hold")
         else:
            return("You cannot check out this book as the ID doesnt belong to you")
    else:
        return("The issue_id is not correct")








def user_summary(db,user_id,use_case):
    '''
    Display the current books on hold
    '''
    if use_case == 'on_hold':
         on_hold = db.execute('''SELECT MAX(issue_id) as issue_id,bc.copy_id,bc.ISBN,b.Title FROM issue i
                  INNER JOIN book_copy bc
                  ON bc.ISBN = i.ISBN
                  INNER JOIN book b
                  ON bc.ISBN = b.ISBN
                  WHERE bc.copy_id=i.copy_id
                  AND bc.Isonhold=1 AND i.user_id=?
                  GROUP BY bc.ISBN''',(user_id,))
         return on_hold
    '''
    Display the books checked out
    '''
    if use_case == 'checked_out':
         checked_out = db.execute('''SELECT MAX(issue_id) AS issue_id,bc.copy_id,bc.ISBN,Issuedate,Returndate FROM issue i
                  INNER JOIN book_copy bc
                  ON bc.ISBN = i.ISBN
                  WHERE bc.copy_id=i.copy_id
                  AND bc.Ischecked=1 AND i.user_id=?
                  GROUP BY bc.ISBN''',(user_id,))
         return checked_out
    '''
    Display the books which are on future hold
    '''
    if use_case == 'fut_hold':
        username = db.execute('SELECT username FROM user WHERE id=?',(user_id,))[0]['username']

        fut_hold_books = db.execute('''SELECT b.ISBN,copy_id,Title FROM book_copy bc
                                       INNER JOIN book b
                                       ON bc.ISBN = b.ISBN
                                       WHERE Fut_req=?''',(username,))
        return fut_hold_books






