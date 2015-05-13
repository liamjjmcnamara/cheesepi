# ensure Influx is spooled up
sleep 10

# define the two required databases
curl -s "http://localhost:8086/db?u=root&p=root" -d "{\"name\": \"cheesepi\"}"
curl -s "http://localhost:8086/db?u=root&p=root" -d "{\"name\": \"grafana\"}"
