import labrad
from Qsim.scripts.pulse_sequences.interleaved_point import interleaved_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit


class InterleavedLinescan(QsimExperiment):
    """
    Scan the 369 laser with the AOM double pass interleaved
    with doppler cooling.
    """

    name = 'Interleaved Line Scan'

    exp_parameters = []
    exp_parameters.append(('InterleavedLinescan', 'interogation_repititions'))
    exp_parameters.append(('InterleavedLinescan', 'line_scan'))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('DipoleInterogation', 'interogation_frequency'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = self.cxn.pulser
        self.dds_channel = '369'

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'photons')  # gives the x and y names to Data Vault
        self.setup_grapher('Interleaved Linescan')
        self.frequencies = self.get_scan_list(self.p.InterleavedLinescan.line_scan, 'MHz')
        for i, freq in enumerate(self.frequencies):
            should_break = self.update_progress(i/float(len(self.frequencies)))
            if should_break:
                break
            freq = WithUnit(freq, 'MHz')
            self.program_pulser(freq)

    def program_pulser(self, freq):
        self.p['DipoleInterogation.interogation_frequency'] = freq
        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_single()
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        time_tags = self.pulser.get_timetags()
        counts = len(time_tags)
        self.pulser.reset_timetags()
        self.dv.add(freq['MHz'], counts)

    def finalize(self, cxn, context):
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = InterleavedLinescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
