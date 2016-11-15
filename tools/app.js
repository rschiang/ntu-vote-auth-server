var express = require('express'),
    app = express(),
    http = require('http'),
    server = http.createServer(app);
var parseString = require('xml2js').parseString;
const bodyParser = require('body-parser');
const xml2js = require('xml2js');
const iconv  = require('iconv-lite');

app.use(bodyParser.raw({ type: '*/xml' }));

var memory = { }

const co = ['', '文學院', '理學院', '社會科學院', '醫學院', '工學院', '生物資源暨農學院', '管理學院', '公衛學院', '電機資訊學院']

app.post('/seqServices/stuinfoByCardno', function(req, res, next) {

    // req.body contains the unparsed xml in buffer
    //  console.log(req.body);

    resp = {
        STUINFO: {
            VERS: '1.00',
            WEBOK: 'NO',
            ERROR: ''
        }
    };

    var unicode = iconv.decode(req.body, 'big5');


    parseString(unicode, function(err, result) {
        // console.log(result);
        if ("STUREQ" in result) {    
            var pChars = ['B', 'T', 'E', 'A', 'C', 'D', 'F', 'Q', 'P', 'R', 'K', 'L'];
            var college = [1010, 1011, 1020, 1030, 1040, 1050, 1060, 1070, 1090, 2010, 2020, 2030, 2040, 2070, 2080, 2090, 3020, 3021, 3022, 3023, 3030, 3050, 3051, 3052, 3100, 4010, 4010, 4020, 4030, 4031, 4040, 4060, 4080, 4090, 5010, 5010, 5010, 5010, 5010, 5010, 5020, 5040, 5050, 5050, 5050, 5050, 5050, 5070, 6010, 6020, 6030, 6031, 6032, 6050, 6050, 6050, 6050, 6050, 6051, 6052, 6053, 6054, 6060, 6060, 6060, 6070, 6080, 6080, 6080, 6080, 6080, 6090, 6100, 6100, 6100, 6101, 6102, 6110, 6110, 6110, 6110, 6120, 6130, 7010, 7011, 7011, 7012, 7020, 7030, 7040, 7050, 8010, 9010, 9020];

            var stuNO = 'B03' + college[Math.floor(Math.random() * 93)].toString() + '0' + (Math.floor(Math.random() * 94)).toString();
            //pChars[Math.floor(Math.random() * 11)] + '03' + college[Math.floor(Math.random() * 93)].toString() + '0' + (Math.floor(Math.random() * 94)).toString();

            if (result.STUREQ.CARDNO in memory) { 
                stuNO = memory[result.STUREQ.CARDNO]; 
            } else {
                memory[result.STUREQ.CARDNO] = stuNO;
            }

            switch (stuNO[0]) {
                case 'B': resp.STUINFO['STUTYPE'] = '學士班'; break;
                case 'T': resp.STUINFO['STUTYPE'] = '學士班交換訪問生'; break;
                case 'E': resp.STUINFO['STUTYPE'] = '進修學士班'; break;
                case 'A': resp.STUINFO['STUTYPE'] = '碩士交換訪問生'; break;
                case 'C': resp.STUINFO['STUTYPE'] = '博士交換訪問生'; break;
                case 'D':
                case 'F':
                case 'Q':
                          resp.STUINFO['STUTYPE'] = '博士生'; break;
                case 'P':
                case 'R': resp.STUINFO['STUTYPE'] = '碩士生'; break;
                case 'K': resp.STUINFO['STUTYPE'] = '高中預修生'; break;
                case 'L': resp.STUINFO['STUTYPE'] = '國際華語學員'; break;
                default: resp.STUINFO['STUTYPE'] = 'Unknown'; break;
            }

            resp.STUINFO['COLLEGE'] = co[stuNO[3]-'0'];
            resp.STUINFO['STUID'] = stuNO;
            resp.STUINFO['DPTCODE'] = 1010;
            resp.STUINFO['INCAMPUS'] = true;
            resp.STUINFO['WEBOK'] = 'OK';
        } else {
            resp.STUINFO.ERROR = 'STUREQ not found!';
        }
    });

    console.log(resp.STUINFO);

    var builder = new xml2js.Builder({xmldec : { 'version': '1.0', 'encoding': 'Big5'} } );
    var xml = builder.buildObject(resp);

    xml = iconv.encode(xml, 'big5');
    res.set('Content-Type', 'application/xml');
    res.send(xml);
});
console.log('ACA simulator listen at port 3000')
server.listen(3000);
