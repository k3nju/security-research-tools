import immlib
import pefile

import os
import traceback
from collections import namedtuple

ExportedEntry = namedtuple("ExportedEntry", ["name", "address"])

class TargetDLL:
    def __init__(self, dll):
        self.filename = os.path.basename(dll.lower())
        if not self.filename.endswith("dll"):
            self.filename = self.filename + ".dll"
        self._resolve_exports()

    def _resolve_exports(self):
        dbg = immlib.Debugger()
        mod = dbg.getModule(self.filename)
        if not mod:
            raise Exception("{} is not loaded".format(self.filename))
        
        path = mod.getPath()
        pe = pefile.PE(path)
        dll_name = os.path.splitext(os.path.basename(path))[0]
        
        self.exporteds = []
        for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            name = "{}.{}".format(dll_name, e.name)
            addr = dbg.getAddress(name)
            if addr == -1:
                dbg.log("failed to get address of {}".format(name))
                continue

            self.exporteds.append(ExportedEntry(name, addr))

class DLLHook(immlib.LogBpHook):
    def __init__(self, exp):
        immlib.LogBpHook.__init__(self)
        self.__exp = exp
        self.__dbg = immlib.Debugger()

    def hook(self):
        self.add(self.__exp.name, self.__exp.address)
        self.__dbg.setComment(self.__exp.address, self.__exp.name);
        self.__dbg.log(
            "hooked 0x{:08x} {}".format(self.__exp.address, self.__exp.name),
            address = self.__exp.address)

    def run(self, regs):
        eip = regs["EIP"]
        self.__dbg.log("{0:08x} {1}".format(eip, self.__exp.name), address = eip)

def usage(dbg):
    dbg.log("!hookexports <target dll>    (hook exported functions from <target dll>)")
        
def main(args):
    dbg = immlib.Debugger()
    
    dll = args[0]
    
    try:
        target_dll = TargetDLL(dll)
        for exp in target_dll.exporteds:
            hooker = DLLHook(exp)
            hooker.hook()
    except:
        for line in traceback.format_exc().split("\n"):
            dbg.log(line)
        return "NG!"
    
    return ""

