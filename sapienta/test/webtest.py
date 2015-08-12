import os

import flask
import logging

from flask_socketio import SocketIO,emit
import testsplitter

app = flask.Flask("webtest")
app.config['SECRET_KEY'] = 'partridge'
app.config['DEBUG'] = True

socketio = SocketIO(app)

logging.basicConfig()

test_papers = []

def collect_papers():
    """Collect together papers that exist in the test corpus"""
    
    
    print "collecting papers"
    nosentsDir = os.path.join(testsplitter.TEST_FILES_PATH, "noSents")
    
    for root,dirs,files in os.walk(nosentsDir):
            
        for file in files:
            if file.endswith(".xml"):
                path = os.path.join(root,file)
                yield {'fullpath' : path, 
                       'name': file, 
                       'manual_sents' : '-', 
                       'auto_sents' : '-', 
                       'sssplit_sents' : '-', 
                       'match' : '-' ,
                       'paper_id' : os.path.splitext(file)[0]
                }


@socketio.on('connect', namespace='/sapienta')
def open_socketio():
    print ('Client connected!')
    
@socketio.on('inspect-paper', namespace='/sapienta')
def inspect_paper(paperid):
    print paperid
    
    manualSents,mwords = testsplitter.getManualSentences(paperid)
    newSents,awords    = testsplitter.getSplitSentences(paperid, None)
    
    emit('paper-inspect-result', {'manual' : manualSents, 'mwords':mwords, 'auto' : newSents, 'awords' : awords})
    
@socketio.on('runsplitter', namespace='/sapienta')
def run_splitter():
    global test_papers
    
    totalSentences = 0
    totalMatches = 0
    
    for paper in test_papers:
        newSplitResults, splitWords    = testsplitter.getSplitSentences(paper['paper_id'], None)
        ssSplitResults     = testsplitter.getSSSplitResult(paper['paper_id'])
        manualSplitResults, manWords = testsplitter.getManualSentences(paper['paper_id'])
        
        paper['auto_sents'] = len(newSplitResults)
        paper['sssplit_sents'] = len(ssSplitResults)
        paper['manual_sents'] = len(manualSplitResults)
        
        matches,sentcount,matchpercent =  testsplitter.compareSents(newSplitResults, manualSplitResults)
        
        totalSentences += sentcount
        totalMatches += matches
        
        if matchpercent > 75:
            colclass = "bg-success"
        elif matchpercent > 50:
            colclass = "bg-warning"
        else:
            colclass = "bg-danger"
            
        paper['match'] = "<p class=\"%s\">%d</p>" %(colclass,matchpercent)
        
        emit("paper_updated", paper)
    
    emit("test_finished", {'totalpercent' : (totalMatches * 100 / totalSentences) })

@app.route("/refresh_papers")
def refresh_test_papers():
    global test_papers
    
    test_papers = list(collect_papers())
    
    return flask.jsonify(papers=test_papers)

@app.route("/")
def index():
    global test_papers
    
    if(len(test_papers) < 1):
        test_papers = list(collect_papers())
    
    return flask.render_template("index.html", papers=test_papers)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
    #app.run("0.0.0.0", 5000, True);
    