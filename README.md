
Introduction to the source files for the CheesePI infrastructure.

# Install

To download a CheesePi distribution execute the following command

`sudo rsync -avzhe ssh  pi@grayling.sics.se:dist/* /usr/local/cheesepi/`

This will leave scripts in  */user/local/cheesepi* directory. To install
the database and crontab jobs that will enable storing and measuring 
of your network.


# Repository structure

dist/ is the directory that will be placed at /usr/local/cheesepi
server/ holds scripts that run on our server
