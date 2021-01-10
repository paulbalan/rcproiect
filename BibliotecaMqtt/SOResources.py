#Functii SO
import psutil
#trebuie instalat psutil-ul
def ProcessorPercent():
    return str(psutil.cpu_percent(interval=1))+"%"
def ProcessorFreq():
    return str(psutil.cpu_freq().current)+" Hz"
def Memory():
    mem=psutil.virtual_memory().total
    mem /= 10**9
    return str(mem)[0:4]+' GB'

def UsedMemory():
    Memory=psutil.virtual_memory()
    memPercent=Memory.percent
    mem=Memory.used
    metric=" GB"
    mem/= 10**9

    return str(memPercent)+"%"
def DiskUsage():
    disks=psutil.disk_partitions(True)
    total = 0
    used = 0

    for disk in disks:
        if disk.fstype =="NTFS" :
            temp=psutil.disk_usage(disk.device)
            total+=temp.total
            used+=temp.used
    metric = " GB"
    total /= 10 ** 9
    used /= 10**9

    return str(int(used))+metric+" used"

