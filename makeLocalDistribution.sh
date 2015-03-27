# cd to the directory this file is in
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd $DIR

# ensure we have the most recent commit from the repos
git pull

# place a commit SHA-1 in the distribution dir
git log --pretty=format:'%h' -n 1 > dist/version
echo >> dist/version


# Run tests, make sure the code works
./testDistribution.py
# if it failed, whine and exit
if [ $? -ne 0 ]; then
	echo "Tests failed! Not pushing code"
else
	# take the current version of the repos and place it on the distribution server
	# for the Pis to download from.
	sudo rsync -avzhe ssh dist/* /usr/local/cheesepi/
fi
