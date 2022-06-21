# Library-Management-System

## The project is a web application which allows users to access a Library which is managed online.
###The user needs to register to the library portal to gain access to the various facilities available.
###The main display page varies depending on whether a library member has logged in or an admin of the library has logged in.
###The library member can perform the following tasks:
- Search for books
- Place a hold on the book
- Checkout a book
- Extend a book
- Place a future hold on book is not available currently
- Return a book
- Total summary for the user

###The admin can perform the following tasks:
-View the list of damaged books
-View the list of debarred students
-View the most frequent users
-View the most popular books
-View the list of overdue members

###The database is initially created with some valid values put in.It is a SQL database which was tested and created using SQL server.
###The code is written in python using Flask and SQlite.
###The templates are designed using HTML and CSS.

###To create a database run the following command in the same folder:

###sqlite3 lib_mn.db -init Library_management.sql
###This creates the database.
###Further details about the project are present in *Assumptions.txt* file

