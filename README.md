# Udacity Item Catalog

A simple web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users have the ability to post, edit, and delete their own items.

## Set Up

1. You need a command line program. I recommend [Git Bash](https://gitforwindows.org/). 
2. Clone the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).    
3.  Look for the ***catalog*** folder and replace it with the contents of this respository.
    

## Usage

Launch the Vagrant VM from inside the ***vagrant*** folder with:

`vagrant up`

Then access the shell with:

`vagrant ssh`

Then move inside the ***catalog*** folder:

`cd /vagrant/catalog`

Then run the application:

`python mylibrary.py`

After the last command you are able to browse the application at this URL:

`http://localhost:8000/`

***You will have to log in to create your own library to be able to use the
edit/delete functionality of the site.  A starter library is in the database
but you cannot modify that library.***
