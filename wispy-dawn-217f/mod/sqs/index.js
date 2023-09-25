var aws4 = require("aws4")

module.exports.postToQueue = async function (Region, msg, queueName, SECRETKEY, ACCESSKEYID) { 
    let hostName = 'sqs.' + Region + '.amazonaws.com'
    let Path = queueName + '/?Action=SendMessage&MessageBody=' + msg
    var opts = {
          service: 'sqs',
          region: Region,
          path: Path,
          Host: hostName,
          signQuery: true
          }
    aws4.sign(opts, { secretAccessKey: SECRETKEY, accessKeyId: ACCESSKEYID })
    var URL = 'https://' + opts.Host + opts.path
    var response = await fetch(URL);
    return (response)
          }

