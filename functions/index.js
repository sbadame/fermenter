const runtimeOpts = {
  timeoutSeconds: 5 * 60,
  memory: '1GB'
}
const PAGE_SIZE = 100000;
const THERMS = {
  'In water': 'Water',
  'In fridge': 'Fridge',
  'Garage': 'Garage'
};

const functions = require('firebase-functions');
const {Storage} = require('@google-cloud/storage');
const storage = new Storage();
const gcsFile = storage.bucket(JSON.parse(process.env.FIREBASE_CONFIG).storageBucket).file('log.json');

// Initialize the Firebase application with admin credentials
const admin = require('firebase-admin');
admin.initializeApp();

const fs = admin.firestore();
fs.settings({timestampsInSnapshots: true});

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

function queryTempLogEntries() {
  const query = fs.collection("logentries").orderBy('timestamp').limit(PAGE_SIZE);
  return paginate(query).then(results => {
    var fireLogs = [];
    results.forEach(doc => {
      var data = doc.data();
      var f = (data.temperature_celsius * (9.0/5.0)) + 32;
      fireLogs.push([data.timestamp.seconds, THERMS[data.thermometer_name], data.status, f]);
    });
    return fireLogs;
  });
}

function queryControllerLogEntries() {
  return fs.collection('controller_logentries').orderBy('timestamp').get().then(results => {
    const entries = results.docs.map(d => d.data());
    for (let entry of entries) {
      entry['timestamp'] = entry['timestamp']['_seconds'];
    }
    return entries;
  });
}

exports.updateCache = functions.runWith(runtimeOpts).firestore.document('ui/upload').onWrite(() => {
  return Promise.all([queryTempLogEntries(), queryControllerLogEntries()]).then(results => {
    const json = JSON.stringify({'temp_logs': results[0], 'controller_state': results[1]});
    const writer = gcsFile.createWriteStream({resumable: false});
    writer.write(json);
    writer.end();
    return 0;
  });
});
