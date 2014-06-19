from Qsim.clients.qtui.switch import QCustomSwitchChannel
from twisted.internet.defer import inlineCallbacks, returnValue
from common.clients.connection import connection
from PyQt4 import QtGui
from switch_client_config import switch_config

class switchclient(QtGui.QWidget):
    


    def __init__(self, reactor, parent = None):
        """initializels the GUI creates the reactor 
            and empty dictionary for channel widgets to 
            be stored for iteration. also grabs chan info
            from wlm_client_config file 
        """ 
        super(switchclient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor     
        self.d = {} 
        self.chaninfo = switch_config.info     
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the wavemeter computer and
        connects incoming signals to relavent functions
        
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name = "switch client")
        self.server = yield self.cxn.arduinottl
        
        self.initializeGUI()
        
    @inlineCallbacks
    def initializeGUI(self):  
    
        layout = QtGui.QGridLayout()
        for chan in self.chaninfo:
            port = self.chaninfo[chan][0]
            position = self.chaninfo[chan][1]
            inverted = self.chaninfo[chan][2]
            
            widget = QCustomSwitchChannel(chan)  

            widget.TTLswitch.setChecked(True)
            widget.TTLswitch.toggled.connect(lambda state = widget.TTLswitch.isDown(), port = port  : self.changeState(state, port))            
            self.d[port] = widget
            layout.addWidget(self.d[port])
        self.setLayout(layout)
        yield None
        
    @inlineCallbacks
    def changeState(self, state, chan):
        yield self.server.ttl_output(chan, state)

    def closeEvent(self, x):
        self.reactor.stop()
        
        
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    switchWidget = switchclient(reactor)
    switchWidget.show()
    reactor.run()
        
        