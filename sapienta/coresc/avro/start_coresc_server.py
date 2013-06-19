'''
Created on 2 Apr 2012

@author: grabmuel

export PYTHONPATH=/homes/grabmuel/avro/avro-1.6.3/src:/homes/grabmuel/eclipse/CoreSC:/nfs/research2/textmining/grabmuel/aho/coresc/crfsuite/usr_local_lib/python2.7/dist-packages:/nfs/research2/textmining/grabmuel/aho/coresc/python-suds-0.4
export LD_LIBRARY_PATH=/nfs/research2/textmining/grabmuel/aho/coresc/crfsuite/usr_local_lib
'''

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import avro.ipc as ipc
import avro.protocol as protocol
import avro.schema as schema
from docparser import Document, Header, Paragraph, Sentence
from crf import Tagger
import logging
import pdb

logging.basicConfig()
logger = logging.getLogger('avro_server')
logger.setLevel(logging.INFO)

PROTOCOL = protocol.parse(open("/homes/grabmuel/eclipse/luna/src/main/java/uk/ac/ebi/tm/luna/avro/coresc.avpr").read())
tagger = Tagger('/nfs/research2/textmining/grabmuel/aho/coresc/crfsuite/a.model')

class Responder(ipc.Responder):
    def __init__(self):
        ipc.Responder.__init__(self, PROTOCOL)

    def invoke(self, msg, req):
        if msg.name == 'send':
            reqDoc = req['document']
            #create 'proper' document instance from avro type document instance in request
            doc = Document()
            for reqHeader in reqDoc['headers']:
                header = Header()
                doc.addHeader(header)
                for reqPara in reqHeader['paragraphs']:
                    para = Paragraph()
                    header.addParagraph(para)
                    for reqSent in reqPara['sentences']:
                        content = reqSent['content']
                        sent = Sentence()
                        sent.addText(content)
                        para.addSentence(sent)
            #get CoreSC sentence labels via the tagger
            labels, probabilities = tagger.getSentenceLabelsWithProbabilities(doc)
            logger.info('tagger returned labels: %s', labels)
            return list(labels)
        else:
            raise schema.AvroException("unexpected message:", msg.getname())
        
class MailHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.responder = Responder()
        call_request_reader = ipc.FramedReader(self.rfile)
        call_request = call_request_reader.read_framed_message()
        resp_body = self.responder.respond(call_request)
        self.send_response(200)
        self.send_header('Content-Type', 'avro/binary')
        self.end_headers()
        resp_writer = ipc.FramedWriter(self.wfile)
        resp_writer.write_framed_message(resp_body)        

server_addr = ('iskra.ebi.ac.uk', 9090)

if __name__ == '__main__':
    server = HTTPServer(server_addr, MailHandler)
    server.allow_reuse_address = True
    logger.info('listening on port 9090')
    server.serve_forever()
