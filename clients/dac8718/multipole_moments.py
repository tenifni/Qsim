
class MultipoleMoments(object):
    """
    Electric potential multipole moments to second order.

    The DAC will change these values independently, giving orthogonal control
    over the DC electric field.  Follows the German diploma thesis naming
    convention.
    """

    def __init__(self):
        # Monpole moment
        self.M_0 = None
        # Dipole moments
        self.M_1 = None
        self.M_2 = None
        self.M_3 = None
        # Quadrupole moments
        self.M_4 = None
        self.M_5 = None
        self.M_6 = None
        self.M_7 = None
        self.M_8 = None
        self._set_multipole_dict()

    def _set_multipole_dict(self):
        """
        Useful for getting and setting values by name.
        """
        self._multipole_dict = {}
        self._multipole_dict['M_0'] = self.M_0
        self._multipole_dict['M_1'] = self.M_1
        self._multipole_dict['M_2'] = self.M_2
        self._multipole_dict['M_3'] = self.M_3
        self._multipole_dict['M_4'] = self.M_4
        self._multipole_dict['M_5'] = self.M_5
        self._multipole_dict['M_6'] = self.M_6
        self._multipole_dict['M_7'] = self.M_7
        self._multipole_dict['M_8'] = self.M_8

    def get_value(self, name=None):
        """
        Get multipole value by name.

        Parameters
        ----------
        name: str
        """
        return self._multipole_dict[name]

    def set_value(self, name=None, value):
        """
        Parameters
        ----------
        name: str, name of the multiple moment, 'M_1', for example.
        value: float, voltage value to set multiple moment to.
        """
        self._multipole_dict[name] = value
