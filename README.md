# Test Data
```
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"lane": 1, "position": "first"}'
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"lane": 2, "position": "second"}'
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"lane": 3, "position": "third"}'
curl -X POST http://127.0.0.1:5000/api/v1/results -H "Content-Type: application/json" -d '{"lane": 4, "position": "fourth"}'
```

# Reset
```
curl -X POST http://127.0.0.1:5000/api/v1/reset
```

# Derby Race
- Turn off Mac Firewall
- Set location to "DerbyRace" for fixed ip
- Connect to DerbyRace Wifi if not already connected
- Run `task reset` to flush db
- Run `task dev` to serve the UI
- Load the UI: http://127.0.0.1:5000
