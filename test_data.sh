curl -XPOST http://127.0.0.1:5000/api/v1/reset
sleep 2
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 2}'
sleep 0.1
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 2, "SECOND": 4}'
sleep 0.5
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 2, "SECOND": 4, "Third": 1}'
sleep 0.4
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 2, "SECOND": 4, "Third": 1, "fourth": 3}'