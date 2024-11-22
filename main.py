import pprint

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    import psutil

    print(psutil.cpu_count(logical=False))  # 返回核心数14
    print(psutil.cpu_count())  # 进程数20
    print(psutil.cpu_freq())  # CPU频率
    # scpufreq(current=2600.0, min=0.0, max=2600.0)

    import cpuinfo

    pprint.pprint(cpuinfo.get_cpu_info()['brand_raw'])

    vm = psutil.virtual_memory()
    GB = 1024 * 1024 * 1024
    print(vm.total / GB, "GB")
    # 31.741661071777344 GB
    print(vm.available / GB, "GB")
    # 15.915771484375 GB
    print(vm.percent, "%")
    # 49.9 %
    print(vm.used / GB, "GB")
    # 15.825889587402344 GB
    # print(psutil.swap_memory())  # 返回交换内存
    # sswap(total=5100273664, used=11184832512, free=-6084558848, percent=219.3, sin=0, sout=0)



