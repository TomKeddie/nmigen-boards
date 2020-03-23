import os
import subprocess

from nmigen.build import *
from nmigen.vendor.lattice_ecp5 import *
from .resources import *


__all__ = ["ECP55GEVNPlatform"]


class ECP55GEVNPlatform(LatticeECP5Platform):
    device      = "LFE5UM5G-85F"
    package     = "BG381"
    speed       = "8"
    default_clk = "clk12"
    default_rst = "rst"

    def __init__(self, *, VCCIO1="2V5", VCCIO6="3V3", **kwargs):
        """
        VCCIO1 is connected by default to 2.5 V via R100 (can be set to 3.3 V by disconnecting
        R100 and connecting R105)
        VCCIO6 is connected to 3.3 V by default via R99 (can be switched to 2.5 V with R104,
        see page 51 in the ECP5-5G-EVN datasheet)
        """
        super().__init__(**kwargs)
        assert VCCIO1 in ("3V3", "2V5")
        assert VCCIO6 in ("3V3", "2V5")
        self._VCCIO1 = VCCIO1
        self._VCCIO6 = VCCIO6

    def _vccio_to_iostandard(self, vccio):
        if vccio == "2V5":
            return "LVCMOS25"
        if vccio == "3V3":
            return "LVCMOS33"
        assert False

    def bank1_iostandard(self):
        return self._vccio_to_iostandard(self._VCCIO1)

    def bank6_iostandard(self):
        return self._vccio_to_iostandard(self._VCCIO6)

    resources   = [
        Resource("rst", 0, PinsN("G2", dir="i"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("clk12", 0, Pins("A10", dir="i"),
                 Clock(12e6), Attrs(IO_TYPE="LVCMOS33")),

        *LEDResources(pins="A13 A12 B19 A18 B18 C17 A17 B17", invert=True,
                      attrs=Attrs(IO_TYPE=bank1_iostandard)),
        *ButtonResources(pins="P4", invert=True,
                         attrs=Attrs(IO_TYPE=bank6_iostandard)),
        *SwitchResources(pins={1: "J1", 2: "H1", 3: "K1"}, invert=True,
                         attrs=Attrs(IO_TYPE=bank6_iostandard)),
        *SwitchResources(pins={4: "E15", 5: "D16", 6: "B16", 7: "C16", 8: "A16"}, invert=True,
                         attrs=Attrs(IO_TYPE=bank1_iostandard)),

        Resource("serdes", 0,
            Subsignal("tx", DiffPairs("W4", "W5", dir="o")),
            Subsignal("rx", DiffPairs("Y5", "Y6", dir="i")),
        ),
        Resource("serdes", 1,
            Subsignal("tx", DiffPairs("W8", "W9", dir="o")),
            Subsignal("rx", DiffPairs("Y7", "Y8", dir="i")),
        ),
        Resource("serdes", 2,
            Subsignal("tx", DiffPairs("W13", "W14", dir="o")),
            Subsignal("rx", DiffPairs("Y14", "Y15", dir="i")),
        ),
        Resource("serdes", 3,
            Subsignal("tx", DiffPairs("W17", "W18", dir="o")),
            Subsignal("rx", DiffPairs("Y16", "Y17", dir="i")),
        ),

        Resource("serdes_clk", 0, DiffPairs("Y11", "Y12", dir="i")),
        Resource("serdes_clk", 1, DiffPairs("Y19", "W20", dir="i")), # 200 MHz

        # TODO: add other resources
    ]
    connectors  = [
        # TODO: add connectors
    ]

    @property
    def file_templates(self):
        return {
            **super().file_templates,
            "{{name}}-openocd.cfg": r"""
            interface ftdi
            ftdi_device_desc "Lattice ECP5 Evaluation Board"
            ftdi_vid_pid 0x0403 0x6010
            ftdi_channel 0
            ftdi_layout_init 0xfff8 0xfffb
            reset_config none
            adapter_khz 25000

            jtag newtap ecp5 tap -irlen 8 -expected-id 0x81113043
            """
        }

    def toolchain_program(self, products, name):
        openocd = os.environ.get("OPENOCD", "openocd")
        with products.extract("{}-openocd.cfg".format(name), "{}.svf".format(name)) \
                as (config_filename, vector_filename):
            subprocess.check_call([openocd,
                "-f", config_filename,
                "-c", "transport select jtag; init; svf -quiet {}; exit".format(vector_filename)
            ])


if __name__ == "__main__":
    from .test.blinky import *
    ECP55GEVNPlatform().build(Blinky(), do_program=True)