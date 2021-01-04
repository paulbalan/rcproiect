import psutil


#trebuie instalat psutil-ul
def ProcessorPercent():
    return "CPU usage : "+str(psutil.cpu_percent(interval=1))+"%"
def ProcessorFreq():
    return "CPU frequency: "+str(psutil.cpu_freq().current)+" Hz"

def Memory(param):
    mem=psutil.virtual_memory().total
    if(param=='g'):
        metric=" GB"
        mem/= 10**9
    else:
        if param=='m':
            metric=" MB"
            mem/=10**6
        else:
            if param=='k':
                metric=" KB"
                mem/=10**3
            else:
                metric=" Bytes"


    return "Total memory: "+str(mem)+metric
def UsedMemory(param):
    Memory=psutil.virtual_memory()
    memPercent=Memory.percent
    mem=Memory.used

    if(param=='g'):
        metric=" GB"
        mem/= 10**9
    else:
        if param=='m':
            metric=" MB"
            mem/=10**6
        else:
            if param=='k':
                metric=" KB"
                mem/=10**3
            else:
                metric=" Bytes"


    return "Used memory: "+str(mem)+ metric +" = "+str(memPercent)+"%"

def DiskUsage(param):
    disks=psutil.disk_partitions(True)


    total = 0
    used = 0

    for disk in disks:
        if disk.fstype =="NTFS" :
            temp=psutil.disk_usage(disk.device)
            total+=temp.total
            used+=temp.used

    if (param == 'g'):
        metric = " GB"
        total /= 10 ** 9
        used /= 10**9
    else:
        if param == 'm':
            metric = " MB"
            total /= 10 ** 6
            used /=10**6
        else:
            if param == 'k':
                metric = " KB"
                total /= 10 ** 3
                used /= 10**3
            else:
                metric = " Bytes"
    return "Disk :"+str(int(total))+metric+" total "+ str(int(used))+metric+" used"


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print(
            "Processor:\n"+
            ProcessorPercent()+'\n'+
            ProcessorFreq()+'\n'+
            "Memory:\n"+
            Memory('g')+'\n' +
            UsedMemory('g')+'\n'+
            "Disk:\n"+
            DiskUsage('g')

          )

