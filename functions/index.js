const runtimeOpts = {
  timeoutSeconds: 5 * 60,
  memory: '1GB'
}
const PAGE_SIZE = 100000;

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

function paginate(base_query, last_seen, collector) {
  if (collector === undefined) {
    collector = [];
  }
  if (last_seen !== undefined) {
    base_query = base_query.startAfter(last_seen);
  }
  return base_query.get().then(querySnapshot => {
    if (querySnapshot.empty) {
      return Promise.resolve(collector);
    }
    querySnapshot.forEach(e => collector.push(e));
    const last = collector[collector.length - 1];
    return paginate(base_query, last, collector);
  });
}

exports.updateCache = functions.runWith(runtimeOpts).firestore.document('ui/upload').onWrite(() => {
  const query = fs.collection("logentries").orderBy('timestamp').limit(PAGE_SIZE);
  return paginate(query).then(results => {
    var fireLogs = [];
    results.forEach(doc => {
      var data = doc.data();
      var f = (data.temperature_celsius * (9.0/5.0)) + 32;
      fireLogs.push([data.timestamp.seconds, data.thermometer_name, data.status, f]);
    });
    var compressedLogs = compress(fireLogs);
    return write(compressedLogs);
  });
});
