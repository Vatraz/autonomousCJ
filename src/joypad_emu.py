import pyvjoy


class JoyPad():
    """
    VJoy pad emulation
    """
    MAX_VJOY = 32767
    DEF_VJOY = MAX_VJOY//2

    def __init__(self, device_idx=1):
        self.vjd = pyvjoy.VJoyDevice(device_idx)

    def reset(self):
        self.vjd.reset()
        self.vjd.reset_buttons()

    def raw_analog_pos(self, pos: float) -> int:
        """
        Converts relative analog stick position to the VJoy raw data

        :param pos: Analog stick position <-1, 1>
        """
        return int(self.DEF_VJOY + self.DEF_VJOY * pos)

    def set_wx_axis(self, value: float) -> None:
        """
        Write position data to wx axis

        :param value: Relative analog stick position <-1, 1>, where 0 is the center position
        """
        self.vjd.data.wAxisX(self.raw_analog_pos(value))

    def update(self):
        """
        Updates emulated JoyPad with the current VJoyDevice data
        """
        self.vjd.update()


if __name__ == '__main__':
    jp = JoyPad(device_idx=3213)
