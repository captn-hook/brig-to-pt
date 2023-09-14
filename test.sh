# curl -X POST json from ./daikin.csv

 
curl -X POST -H "Content-Type: application/json" -d '{"csv": $(cat ./daikin.csv), "model": "https://firebasestorage.googleapis.com/v0/b/brig-b2ca3.appspot.com/o/Sites%2FArroyo%2FArroyo.glb", bucket: "brig-b2ca3.appspot.com", "folder": "Sites/Arroyo"}' http://localhost:8080/