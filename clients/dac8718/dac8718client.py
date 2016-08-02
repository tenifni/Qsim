from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui
from PyQt4.Qt import QPushButton
from config.dac_8718_config import dac_8718_config
from electrodes import Electrodes


class dacclient(QtGui.QWidget):

    def __init__(self, reactor, parent=None):
        """initializes the GUI creates the reactor
            and empty dictionary for channel widgets to
            be stored for iteration.
        """
        super(dacclient, self).__init__()
        self.max_bit_value = 2**16 - 1
        self.min_bit_value = 0
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.d = {}
        self.e = {}
        self.topelectrodes = {'DAC 0': 0, 'DAC 1': 1, 'DAC 2': 2, 'DAC 3': 3}
        self.bottomelectrodes = {'DAC 4': 4,  'DAC 5': 5,  'DAC 6': 6, 'DAC 7': 7}
        self.xminuselectrodes = {'DAC 2': 2, 'DAC 6': 6}
        self.xpluselectrodes = {'DAC 0': 0, 'DAC 4': 4}
        self.yminuselectrodes = {'DAC 1': 1, 'DAC 5': 5}
        self.ypluselectrodes = {'DAC 3': 3, 'DAC 7': 7}
        self.electrodes = Electrodes()
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection."""
        from labrad.wrappers import connectAsync
        from labrad.units import WithUnit as U

        self.U = U
        self.cxn = yield connectAsync(name="dac8718 client")
        self.server = yield self.cxn.dac8718_server
        self.reg = yield self.cxn.registry

        try:
            yield self.reg.cd('settings')
            self.settings = yield self.reg.dir()
            self.settings = self.settings[1]
        except:
            self.settings = []

        self.config = dac_8718_config
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):

        layout = QtGui.QGridLayout()

        qBox = QtGui.QGroupBox('DAC Channels')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)
        self.bit_step_size = 10
        self.currentvalues = {}

        self.Ex_label = QtGui.QLabel('E_x')
        self.Ey_label = QtGui.QLabel('E_y')
        self.Ez_label = QtGui.QLabel('E_z')
        self.Ex_squeeze_label = QtGui.QLabel('E_x squeeze')
        self.Ey_squeeze_label = QtGui.QLabel('E_y squeeze')
        self.Ez_squeeze_label = QtGui.QLabel('E_z squeeze')

        for channel_key in self.config.channels:
            name = self.config.channels[channel_key].name
            chan_number = self.config.channels[channel_key].number

            widget = QCustomSpinBox(name, (self.min_bit_value,
                                           self.max_bit_value))

            widget.title.setFixedWidth(120)
            label = QtGui.QLabel('0 V')
            if name in self.settings:
                value = yield self.reg.get(name)
                widget.spinLevel.setValue(value)
                self.currentvalues.update({name: value})
                self.electrodes.set_electrode_value(name=name, value=value)
                self.set_value_no_widgets(value, [name, chan_number])
            else:
                widget.spinLevel.setValue(0.0)
            widget.setStepSize(1)
            widget.spinLevel.setDecimals(0)
            widget.spinLevel.valueChanged.connect(lambda value=widget.spinLevel.value(),
                                                  ident=[name, chan_number]:
                                                  self.setvalue(value, ident))

            self.d[chan_number] = widget
            self.e[chan_number] = label
            subLayout.addWidget(self.d[chan_number],  chan_number, 1)
            subLayout.addWidget(self.e[chan_number], chan_number, 2)

        self.exsqueezeupwidget = QPushButton('X Squeeze increase')
        self.exsqueezedownwidget = QPushButton('X Squeeze decrease')
        self.eysqueezeupwidget = QPushButton('Y Squeeze increase')
        self.eysqueezedownwidget = QPushButton('Y Squeeze decrease')
        self.z_squeeze_up_widget = QPushButton('Z squeeze increase')
        self.z_squeeze_down_widget = QPushButton('Z squeeze decrease')

        self.ezupwidget = QPushButton('Ez increase')
        self.ezdownwidget = QPushButton('Ez decrease')
        self.exupwidget = QPushButton('Ex increase')
        self.exdownwidget = QPushButton('Ex decrease')
        self.eyupwidget = QPushButton('Ey increase')
        self.eydownwidget = QPushButton('Ey decrease')

        self.save_widget = QPushButton('Save current values to Registry')

        self.dipole_res = QCustomSpinBox('Bit step size', (0, 1000))
        self.dipole_res.spinLevel.setValue(10)
        self.dipole_res.setStepSize(1)
        self.dipole_res.spinLevel.setDecimals(0)

        self.exsqueezeupwidget.clicked.connect(self.ex_squeeze_up)
        self.eysqueezeupwidget.clicked.connect(self.ey_squeeze_up)
        self.z_squeeze_up_widget.clicked.connect(self.z_squeeze_up)

        self.exsqueezedownwidget.clicked.connect(self.ex_squeeze_down)
        self.eysqueezedownwidget.clicked.connect(self.ey_squeeze_down)
        self.z_squeeze_down_widget.clicked.connect(self.z_squeeze_down)

        self.ezupwidget.clicked.connect(self.ezup)
        self.ezdownwidget.clicked.connect(self.ezdown)
        self.exupwidget.clicked.connect(self.exup)
        self.exdownwidget.clicked.connect(self.exdown)
        self.eyupwidget.clicked.connect(self.eyup)
        self.eydownwidget.clicked.connect(self.eydown)
        self.dipole_res.spinLevel.valueChanged.connect(self.update_dipole_res)
        self.save_widget.clicked.connect(self.save_to_registry)

        subLayout.addWidget(self.ezupwidget,   0, 5)
        subLayout.addWidget(self.ezdownwidget, 1, 5)
        subLayout.addWidget(self.exupwidget,   3, 6)
        subLayout.addWidget(self.exdownwidget, 3, 3)
        subLayout.addWidget(self.eyupwidget,   2, 5)
        subLayout.addWidget(self.eydownwidget, 4, 5)
        subLayout.addWidget(self.dipole_res,   3, 5)
        subLayout.addWidget(self.save_widget,  5, 5)
        subLayout.addWidget(self.Ex_label,     6, 5)
        subLayout.addWidget(self.Ey_label,     7, 5)
        subLayout.addWidget(self.Ez_label,     8, 5)
        subLayout.addWidget(self.Ex_squeeze_label, 9, 5)
        subLayout.addWidget(self.Ey_squeeze_label, 10, 5)
        subLayout.addWidget(self.Ez_squeeze_label, 11, 5)

        subLayout.addWidget(self.exsqueezeupwidget,   6, 6)
        subLayout.addWidget(self.exsqueezedownwidget, 6, 7)
        subLayout.addWidget(self.eysqueezeupwidget,   7, 6)
        subLayout.addWidget(self.eysqueezedownwidget, 7, 7)
        subLayout.addWidget(self.z_squeeze_up_widget, 8, 6)
        subLayout.addWidget(self.z_squeeze_down_widget, 8, 7)

        self.setLayout(layout)

    @inlineCallbacks
    def ezup(self, isheld):
        for name, dacchan in self.topelectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.bottomelectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def ezdown(self, isheld):
        for name, dacchan in self.bottomelectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.topelectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def exup(self, isheld):
        for name, dacchan in self.xpluselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.xminuselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def exdown(self, isheld):
        for name, dacchan in self.xminuselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.xpluselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def eyup(self, isheld):
        for name, dacchan in self.ypluselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.yminuselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def eydown(self, isheld):
        for name, dacchan in self.yminuselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.ypluselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def ex_squeeze_up(self, isheld):
        for name, dacchan in self.xpluselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.xminuselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def ex_squeeze_down(self, isheld):
        for name, dacchan in self.xpluselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.xminuselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def ey_squeeze_up(self, isheld):
        for name, dacchan in self.ypluselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.yminuselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue >= self.max_bit_value:
                break
            new_value = currentvalue + self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def ey_squeeze_down(self, isheld):
        for name, dacchan in self.ypluselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

        for name, dacchan in self.yminuselectrodes.iteritems():
            currentvalue = self.currentvalues[name]
            if currentvalue <= self.min_bit_value:
                break
            new_value = currentvalue - self.bit_step_size
            yield self.setvalue(new_value, [name, dacchan])

    @inlineCallbacks
    def z_squeeze_up(self, isheld):
        """
        Increase the voltage on all electrodes.
        """
        for name in self.electrodes.z_electrodes:
            bit_value = self.electrodes.get_electrode_value(name)
            if bit_value >= self.max_bit_value:
                break
            new_value = bit_value + self.bit_step_size
            dac_channel = self.electrodes.get_electrode_number(name)
            yield self.setvalue(new_value, [name, dac_channel])

    @inlineCallbacks
    def z_squeeze_down(self, isheld):
        """
        Decrease the voltage on all electrodes.
        """
        for name in self.electrodes.z_electrodes:
            bit_value = self.electrodes.get_electrode_value(name)
            if bit_value <= self.min_bit_value:
                break
            new_value = bit_value - self.bit_step_size
            dac_channel = self.electrodes.get_electrode_number(name)
            yield self.setvalue(new_value, [name, dac_channel])

    @inlineCallbacks
    def setvalue(self, value, ident):
        """
        Parameters
        ----------
        value: float?  - converted to an int
        ident: tuple, (name, chan) where name is a str and chan is an int
        """
        yield self.set_value_no_widgets(value=value, ident=ident)
        channel_number = ident[1]
        # change the GUI display value
        self.d[channel_number].spinLevel.setValue(value)

    @inlineCallbacks
    def set_value_no_widgets(self, value, ident):
        """
        Parameters
        ----------
        value: float?  - converted to an int
        ident: tuple, (name, chan) where name is a str and chan is an int
        """
        name = ident[0]
        channel_number = ident[1]
        value = int(value)
        self._set_electrode_current_value(name, value)
        print "set_value_no_widgets"
        print "\t name:", name
        print "\t channel_number:", channel_number
        print "\t value:", value
        yield self.server.dacoutput(channel_number, value)
        voltage = self.bit_to_volt(bit=value)
        self.e[channel_number].setText(str(voltage))
        self.currentvalues[name] = value
        self.set_dipole_labels()
        self.set_squeeze_labels()

    def bit_to_volt(self, bit):
        voltage = (2.2888e-4*bit - 7.5)
        return voltage

    def _set_electrode_current_value(self, name=None, value=None):
        """
        Set electrode value in the Electrodes class.
        """
        self.electrodes.set_electrode_value(name=name, value=value)

    def set_dipole_labels(self):
        xdipole = self.electrodes.x_dipole_moment
        ydipole = self.electrodes.y_dipole_moment
        zdipole = self.electrodes.z_dipole_moment

        self.Ex_label.setText('Ex = ' + str(xdipole))
        self.Ey_label.setText('Ey = ' + str(ydipole))
        self.Ez_label.setText('Ez = ' + str(zdipole))

    def set_squeeze_labels(self):
        x_squeeze = self.electrodes.x_squeeze_moment
        y_squeeze = self.electrodes.y_squeeze_moment
        z_squeeze = self.electrodes.z_squeeze_moment

        self.Ex_squeeze_label.setText('Ex squeeze = ' + str(x_squeeze))
        self.Ey_squeeze_label.setText('Ey squeeze = ' + str(y_squeeze))
        self.Ez_squeeze_label.setText('Ez squeeze = ' + str(z_squeeze))

    def update_dipole_res(self, value):
        self.bit_step_size = value

    def save_to_registry(self):
        for chan in self.currentvalues:
            self.reg.set(chan, self.currentvalues[chan])

    def closeEvent(self, x):
        print 'Saving DAC values to regisry...'
        self.save_to_registry()
        print 'Saved.'
        self.reactor.stop()


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    dacWidget = dacclient(reactor)
    dacWidget.show()
    reactor.run()  # @UndefinedVariable
