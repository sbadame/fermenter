const runtimeOpts = {
  timeoutSeconds: 2 * 60,
  memory: '1GB'
}

const functions = require('firebase-functions');
const pako = require('pako');

// Initialize the Firebase application with admin credentials
const admin = require('firebase-admin');
admin.initializeApp();

const fs = admin.firestore();
fs.settings({timestampsInSnapshots: true});

function compress(logs) {
  return pako.deflate(JSON.stringify(logs));
}

function write(compressedLogs) {
  return fs.collection('ui').doc('data').update({'gzipped': compressedLogs});
}

exports.updateCache = functions.runWith(runtimeOpts).firestore.document('ui/upload').onWrite((change, context) => {
  return fs.collection("logentries").orderBy('timestamp').get().then((querySnapshot) => {
    var fireLogs = [];
    querySnapshot.forEach((doc) => {
      var data = doc.data();
      var f = (data.temperature_celsius * (9.0/5.0)) + 32;
      fireLogs.push([data.timestamp.seconds, data.thermometer_name, data.status, f]);
    });
    var compressedLogs = compress(fireLogs);
    return write(compressedLogs);
  });
});
