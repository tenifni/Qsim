import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.bright_state_preperation import bright_state_preperation as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment


class BrightStateDetection(QsimExperiment):
    """
    Doppler cool ion the readout bright fidelity
    """

    name = 'Bright State Detection'

    exp_parameters = []
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('BrightStateDetection', 'RunContinuous'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pmt = self.cxn.normalpmtflow
        self.init_mode = self.pmt.getcurrentmode()
        self.pmt.set_mode('Normal')
        self.pulser = self.cxn.pulser
        self.rsg = self.cxn.grapher
        self.prob_ctx = self.dv.context()
        self.hist_ctx = self.dv.context()

    def run(self, cxn, context):

        self.setup_prob_datavault()
        if self.p.BrightStateDetection.RunContinuous == True:
            i = 0
            while True:
                i+=1
                counts = self.program_pulser()
                hist = self.process_data(counts)
                if i % 10 == 0:
                    self.setup_hist_datavault()
                    self.plot_hist(hist)
                self.plot_prob(i, counts)
                should_break = self.update_progress(np.random.random())
                if should_break:
                    break
                self.reload_all_parameters()
                self.p = self.parameters
        else:
            counts = self.program_pulser()
            hist = self.process_data(counts)
            self.setup_hist_datavault()
            self.plot_hist(hist)
            self.plot_prob(0, hist)

    def program_pulser(self):

        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(int(self.p.StateDetection.repititions))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        counts = self.pulser.get_readout_counts()
        self.pulser.reset_readout_counts()
        return counts

    def setup_hist_datavault(self):
        self.dv.cd(['','Bright_State_Detection'], True, context=self.hist_ctx)
        self.dataset_hist = self.dv.new('bright_state_prep', [('run', 'arb u')],
                                        [('Counts', 'Counts', 'num')], context = self.hist_ctx)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hist_ctx)


    def setup_prob_datavault(self):
        self.dv.cd(['', 'Bright_State_Probability'], True, context=self.prob_ctx)
        self.dataset_prob = self.dv.new('fidelity_bright_state_prep', [('run', 'arb u')],
                                        [('Counts', 'Counts', 'num')], context=self.prob_ctx)
        self.rsg.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.prob_ctx)

    def process_data(self, counts):
        data = np.column_stack((np.arange(self.p.StateDetection.repititions), counts))
        y = np.histogram(data[:, 1], int(np.max([data[:, 1].max() - data[:, 1].min(), 1])))
        counts = y[0]
        bins = y[1][:-1]
        if bins[0] < 0:
            bins = bins + .5
        hist = np.column_stack((bins, counts))
        return hist

    def plot_hist(self, hist):
        self.dv.add(hist, context=self.hist_ctx)
        self.rsg.plot(self.dataset_hist, 'Histogram', False)

    def plot_prob(self, num, counts):
        self.thresholdVal = self.p.StateDetection.state_readout_threshold
        prob = len(np.where(counts > self.thresholdVal)[0])/float(len(counts))
        self.dv.add(num, prob, context = self.prob_ctx)

    def finalize(self, cxn, context):
        self.pmt.set_mode(self.init_mode)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = BrightStateDetection(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
