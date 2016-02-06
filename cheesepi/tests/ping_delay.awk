BEGIN {
	while (getline) {
		delay = gensub(/.*time=([0-9]+[\.0-9]*).*/, "\\1", 1, $0)
		if (delay == $0)
			print delay
		else
			printf "%s,", delay
	}
}
