# cd to the directory this file is in
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd $DIR

# ensure we have the most recent commit from the repos
git pull

# place a commit SHA-1 in the distribution dir
git log --pretty=format:'%h' -n 1 > cheesepi/version
echo >> cheesepi/version


# Run tests, make sure the code works
./testDistribution.py
# if it failed, whine and exit
if [ $? -ne 0 ]; then
	echo "Tests failed!"
else
	# take the current version of the repos and place it on the distribution server
	# for the Pis to download from.
	#rsync -avzhe ssh dist/* pi@grayling.sics.se:dist
	tar -czf cheesepi.tar.gz cheesepi/	
fi

echo -e "\nNow copy cheesepi.tar.gz to the distribution location!\n"
