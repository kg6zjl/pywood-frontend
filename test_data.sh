# curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 1}'
# curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 1, "SECOND": 3}'
# curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 1, "SECOND": 3, "Third": 4}'
# curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 1, "SECOND": 3, "Third": 4, "fourth": 2}'

curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 2}'
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 2, "SECOND": 4}'
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 2, "SECOND": 4, "Third": 1}'
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"First": 2, "SECOND": 4, "Third": 1, "fourth": 3}'