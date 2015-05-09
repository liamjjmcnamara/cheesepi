
# Script to package the code from the repository into a tar.gz file
# that can be downloaded by nodes in the CheesePi community 

# cd to the directory that this file is in
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd $DIR

# ensure we have the most recent commit from the repos
git pull

# place a commit SHA-1 in the distribution dir
# this 'version' string will be attached to all data points placed in the DB
git log --pretty=format:'%h' -n 1 > cheesepi/version
echo >> cheesepi/version


# Run tests, make sure the code works
./testDistribution.py
# if it failed, whine and exit
if [ $? -ne 0 ]; then
	echo "Error: Tests failed, not packaging!"
else
	# take the current version of the repos and place it on the distribution server
	# for the Pis to download from.
	#rsync -avzhe ssh dist/* pi@grayling.sics.se:dist
	tar -czf cheesepi.tar.gz cheesepi/
fi

echo -e "\nNow copy cheesepi.tar.gz to the distribution location!\n"
