import os
import subprocess
import shutil

from nmigen.build import *
from nmigen.vendor.lattice_ecp5 import *
from .resources import *


__all__ = ["ButterStickR1_0Platform"]


class ButterStickR1_0Platform(LatticeECP5Platform):
    device      = "LFE5U-25F"
    package     = "BG381"
    speed       = "8"
    default_clk = "clk"
    resources   = [
        Resource("clk", 0, Pins("B12", dir="i"),
                 Clock(30e6), Attrs(IO_TYPE="LVCMOS33")),

        # Used to reload FPGA configuration.
        # Can enter USB bootloader by assigning button 0 to program.
        Resource("program", 0, PinsN("R3", dir="o"), Attrs(IO_TYPE="LVCMOS33")),

##        RGBLEDResource(0, 
##            r="K4", g="M3", b="J3", invert=True,
##            attrs=Attrs(IO_TYPE="LVCMOS33")),

        *ButtonResources(
            pins={0: "U16", 1: "T17" }, invert=True,
            attrs=Attrs(IO_TYPE="SSTL135_I")),

        *SPIFlashResources(0,
            cs_n="R2", clk="U3", cipo="W2", copi="V2", wp_n="Y2", hold_n="W1",
            attrs=Attrs(IO_TYPE="LVCMOS33"),
        ),

        Resource("ddr3", 0,
            Subsignal("rst",     PinsN("E17", dir="o")),
            Subsignal("clk",     DiffPairs("C20 J19", "D19 K19", dir="o"), Attrs(IO_TYPE="SSTL135D_I")),
            Subsignal("clk_en",  Pins("F18 J18", dir="o")),
            Subsignal("cs",      PinsN("J20 J16", dir="o")),
            Subsignal("we",      PinsN("G19", dir="o")),
            Subsignal("ras",     PinsN("K18", dir="o")),
            Subsignal("cas",     PinsN("J17", dir="o")),
            Subsignal("a",       Pins("G16 E19 E20 F16 F19 E16 F17 L20 M20 E18 G18 D18 H18 C18 D17 G20 ", dir="o")),
            Subsignal("ba",      Pins("H16 F20 H20", dir="o")),
            Subsignal("dqs",     DiffPairs("T19 N16", "R18 M18", dir="io"),
                      Attrs(IO_TYPE="SSTL135D_I", TERMINATION="OFF",
                            DIFFRESISTOR="100")),
            Subsignal("dq",      Pins("U19 T18 U18 R20 P18 P19 P20 N20 L19 L17 L16 R16 N18 R17 N17 P17",
                                      dir="io"), Attrs(TERMINATION="75")),
            Subsignal("dm",      Pins("U20 L18", dir="o")),
            Subsignal("odt",     Pins("K20 H17", dir="o")),
                 Attrs(IO_TYPE="SSTL135_I", SLEWRATE="FAST")
        ),

        Resource("eth_rgmii", 0,
            Subsignal("rst",     PinsN("B20", dir="o")),
            Subsignal("mdc",     Pins("A19", dir="o")),
            Subsignal("mdio",    Pins("D16", dir="io")),
            Subsignal("tx_clk",  Pins("E15", dir="o")),
            Subsignal("tx_ctl",  Pins("D15", dir="o")),
            Subsignal("tx_data", Pins("C15 B16 A18 B19", dir="o")),
            Subsignal("rx_clk",  Pins("D11", dir="i")),
            Subsignal("rx_ctl",  Pins("B18", dir="i")),
            Subsignal("rx_data", Pins("A16 C17 B17 A17", dir="i")),
            Attrs(IO_TYPE="LVCMOS25")
        ),
        ULPIResource(0, data="B9 C6 A7 E9 A8 D9 C10 C7",
                     rst="C9", clk="B6", dir="A6", stp="C8", nxt="B8",
                     clk_dir="i", rst_invert=True, attrs=Attrs(IOSTANDARD="LVCMOS18")),
        
##        Resource("ddr3_pseudo_power", 0,
##            # pseudo power pins, leave these at their default value
##            Subsignal("vcc_virtual", PinsN("K16 D17 K15 K17 B18 C6", dir="o")),
##            Subsignal("gnd_virtual", Pins("L15 L16", dir="o")),
##            Attrs(IO_TYPE="SSTL135_II", SLEWRATE="FAST")
##        ),

##        Resource("adc", 0,
##            Subsignal("ctrl",     Pins("G1 F1", dir="o")),
##            Subsignal("mux",      Pins("F4 F3 F2 H1", dir="o")),
##            Subsignal("sense",    DiffPairs("H3", "G3", dir="i"), Attrs(IO_TYPE="LVCMOS33D")),
##            Attrs(IO_TYPE="LVCMOS33")
##        ),
    ]
    connectors = [
        Connector("syzygy", 0, {
            "S0_D0_P":   "G2",
            "S1_D1_P":   "J3",
            "S2_D0_N":   "F1",
            "S3_D1_N":   "K3",
            "S4_D2_P":   "J4",
            "S5_D3_P":   "K2",
            "S6_D2_N":   "J5",
            "S7_D3_N":   "J1",
            "S8_D4_P":   "N2",
            "S9_D5_P":   "L3",
            "S10_D4_N":  "M1",
            "S11_D5_N":  "L2",
            "S12_D6_P":  "N3",
            "S13_D7_P":  "N4",
            "S14_D6_N":  "M3",
            "S15_D7_N":  "P5",
            "S16":       "H1",
            "S17":       "K5",
            "S18":       "K4",
            "S19":       "K1",
            "S20":       "L4",
            "S21":       "L1",
            "S22":       "L5",
            "S23":       "M4",
            "S24":       "N1",
            "S25":       "N5",
            "S26":       "P3",
            "S28":       "P4",
            "C2P_CLK_N": "P2",
            "C2P_CLK_P": "P1",
            "P2C_CLK_N": "G1",
            "P2C_CLK_P": "H2",
        }),
        Connector("syzygy", 1, {
            "S0_D0_P":   "E4",
            "S1_D1_P":   "A4",
            "S2_D0_N":   "D5",
            "S3_D1_N":   "A5",
            "S4_D2_P":   "C4",
            "S5_D3_P":   "B2",
            "S6_D2_N":   "B4",
            "S7_D3_N":   "C2",
            "S8_D4_P":   "A2",
            "S9_D5_P":   "C1",
            "S10_D5_N":  "D1",
            "S11_D4_N":  "B1",
            "S12_D6_P":  "F4",
            "S13_D7_P":  "D2",
            "S14_D6_N":  "E3",
            "S15_D7_N":  "E1",
            "S16":       "B5",
            "S17":       "E5",
            "S18":       "F5",
            "S19":       "C5",
            "S20":       "B3",
            "S21":       "A3",
            "S22":       "D3",
            "S23":       "C3",
            "S24":       "H5",
            "S25":       "G5",
            "S26":       "H3",
            "S27":       "H4",
            "C2P_CLK_N": "F3",
            "C2P_CLK_P": "G3",
            "P2C_CLK_N": "E2",
            "P2C_CLK_P": "F2",
        }),
        Connector("syzygy", 2, {
            "S0":        "C11",
            "S1":        "B11",
            "S2":        "D6",
            "S3":        "D7",
            "S4":        "E6",
            "S5":        "E7",
            "S6":        "D8",
            "S7":        "E8",
            "S8":        "E10",
            "S9":        "D10",
            "RX0_N":     "Y6",
            "RX0_P":     "Y5",
            "RX1_N":     "Y8",
            "RX1_P":     "Y7",
            "RX2_N":     "Y15",
            "RX2_P":     "Y14",
            "RX3_N":     "Y17",
            "RX3_P":     "Y16",
            "TX0_N":     "W5",
            "TX0_P":     "W4",
            "TX1_N":     "W9",
            "TX1_P":     "W8",
            "TX2_N":     "W14",
            "TX2_P":     "W13",
            "TX3_N":     "W18",
            "TX3_P":     "W17",
            "C2P_CLK_N": "B10",
            "C2P_CLK_P": "A9",
            "P2C_CLK_N": "A11",
            "P2C_CLK_P": "A10",
            "REFCLK_N":  "Y12",
            "REFCLK_P":  "Y11",
        }),
    ]

    @property
    def required_tools(self):
        return super().required_tools + [
            "dfu-suffix"
        ]

    @property
    def command_templates(self):
        return super().command_templates + [
            r"""
            {{invoke_tool("dfu-suffix")}}
                -v 1209 -p 5af0 -a {{name}}.bit
            """
        ]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = dict(ecppack_opts="--compress --freq 38.8")
        overrides.update(kwargs)
        return super().toolchain_prepare(fragment, name, **overrides)

    def toolchain_program(self, products, name):
        dfu_util = os.environ.get("DFU_UTIL", "dfu-util")
        with products.extract("{}.bit".format(name)) as bitstream_filename:
            subprocess.check_call([dfu_util, "-D", bitstream_filename])


if __name__ == "__main__":
    from .test.blinky import *
    ButterStickR1_0Platform().build(Blinky(), do_program=True)
