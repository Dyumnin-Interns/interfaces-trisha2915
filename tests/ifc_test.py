import cocotb
from cocotb.decorators import coroutine
from cocotb.triggers import (Event, RisingEdge, ReadOnly, Timer, NextTimeStep, Edge)
from cocotb_bus.drivers import BusDriver
from cocotb.result import ReturnValue, TestError
import random


def sb_fn(actual_value):
    assert actual_value == exp_value, "Scoreboard Matching Failed"


@cocotb.test()
async def ifc_test(dut):
    global exp_value
    
    #a = (10010110, 11100010)
    exp_value = (101111000)

    dut.RST_N.value = 1
    await Timer(1, 'ps')
    dut.RST_N.value = 0
    await Timer(1, 'ps')
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1

    dut.din_en.value = 1
    dut.len_en.value = 1
    dut.len_value.value = 2
    await Timer(1,'ns')
    dut.din_rdy = 1
    adrv = InputDriver(dut, 'din_value', dut.CLK)
    OutputDriver(dut, 'dout_value', dut.CLK, sb_fn)

    for i in range(2):
        adrv._driver_send(2)

    
    await(Timer(2,'ns'))

class InputDriver(BusDriver):
    _signals = ["din_rdy", "din_en", "din_value"]

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.din_en= 0
        self.clk = clk
        

    async def _driver_send(self,value,sync=True):
        for i in range(random.randint(0,20)):
            await RisingEdge(self.clk)
        if self.bus.din_rdy != 1:
            await RisingEdge(self.bus.din_rdy)
        self.bus.din_en.value = 1
        self.bus.din_value = value
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.din_en.value = 0
        await NextTimeStep()

class OutputDriver(BusDriver):
    _signals = ['dout_value', 'dout_rdy', 'dout_en']

    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.dout_en = 0
        self.clk = clk
        self.callback = sb_callback

    async def _driver_send(self,value,sync=True):
        while True:
            for i in range(random.randint(0,20)):
                await RisingEdge(self.clk)
            if self.bus.dout_rdy.value != 1:
                await RisingEdge(self.clk)
            self.bus.dout_en.value = 1
            await ReadOnly()
            self.callback(self.bus.dout_value.value)
            await RisingEdge(self.clk)
            self.bus.dout_en.value = 0
            await NextTimeStep()
            self.bus.dout_en.value = 0




