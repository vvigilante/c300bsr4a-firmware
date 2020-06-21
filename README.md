# C300BSR4A v2
Original firmware dump and installation of DD-Wrt and OpenWrt on this wireless access point by Conceptronic.

You will need some linux. I used Ubuntu 18.04 on WSL.

## Connect serial
Needs soldering on the board. There are two round spots on the back of the board for rx and tx.
You find the image here:
https://forum.dd-wrt.com/phpBB2/viewtopic.php?t=70848

The parameters are:
57600.8, N, 1

## Backup your original firmware
### Setup
On the device there is less than the bare minimum, both in the uboot section and in the linux section.
My plan is to image the flash via linux, so we need to transfer some tools (dd and netcat would be nice).

We obtain a binary version of busybox that contains those tools [here](https://busybox.net/downloads/binaries/1.16.1/busybox-mipsel) but unfortunately we cannot download it directly on the device. Download it on your machine and use *encode.py* to transform it into a series of echo statements to execute on the remote device.

```bash
# on the local machine
wget https://busybox.net/downloads/binaries/1.16.1/busybox-mipsel
python3 encode.py busybox-mipsel > createbb.sh
```

Serial connection is unreliable and is bound to fail if we aim to transfer so much data, but telnetd is available on the device, so connect via serial and run
```bash
# on the remote device, via serial
telnetd -l /bin/sh
```

Assuming that the device ip is *10.10.10.199* run
```bash
# on the local machine
telnet 10.10.10.199
cd /tmp/
```
and paste the contents of *createbb.sh*

Wait for it to finish and then
```bash
# on the remote device, via telnet
chmod +x busybox-mipsel
```

### Backup the firmware
Run
```bash
# on the local machine
nc -l -p 62222 | dd of=mtd0-dump
```
Assuming that the ip of your local machine is *10.10.10.118* run
```bash
# on the remote device
/tmp/busybox-mipsel dd if=/dev/mtdblock0 | /tmp/busybox-mipsel nc -w 3 10.10.10.118 62222
```
Do the same for partitions 0, 1, 2, 3

### Check that the firmware is correctly dumped

You should have this flash layout on the device
```
0x00000000-0x00030000 : "uboot"					(size 03 0000)
0x00030000-0x00040000 : "uboot-config"			(size 01 0000)
0x00040000-0x00050000 : "factory-defaults"		(size 01 0000)
0x00050000-0x00120000 : "linux"					(size 0D 0000)
0x00120000-0x00400000 : "rootfs"				(size 2E 0000)
```
where
* */dev/mtdblock0* is uboot
* */dev/mtdblock1* is uboot-config
* */dev/mtdblock2* is factory-defaults
* */dev/mtdblock3* is linux + rootfs

At the end you should have 4 files
* *mtd0-dump* 196608 bytes
* *mtd1-dump* 65536 bytes
* *mtd2-dump* 65536 bytes
* *mtd3-dump* 3866624 bytes
The sum of those is the size of the flash, 4194304‬ bytes = 0x40 0000 bytes = 4MB.

The command 
```bash
# on the local machine
file mtd3-dump
```
should give the following output:
```
mtd3-dump: u-boot legacy uImage, linkn Kernel Image, Linux/MIPS, OS Kernel Image (lzma), 2204781 bytes, Fri Apr  9 14:07:31 2010, Load Address: 0x80000000, Entry Point: 0x80366000, Header CRC: 0x9FDFE333, Data CRC: 0xA9241625
```


## Install dd-wrt
Find your firmware [here](https://forum.dd-wrt.com/phpBB2/viewtopic.php?p=324454#324454)
Put the file in the root directory of your tftp server (I used MobaXTerm for Windows). Name it firmware.bin for simplicity.

You will not be able to run the dd-wrt firmware without flashing due to the fact that dd-wrt wants to mount their rootfs and it needs to be on flash.


Here is the expected output:
  <details>
    <summary><i>click to expand</i></summary>
  
```
U-Boot 1.1.3 (Dec  8 2009 - 13:38:58)

Board: Ralink APSoC DRAM:  32 MB
relocate_code Pointer at: 81fb0000
flash_protect ON: from 0xBF000000 to 0xBF01D663
flash_protect ON: from 0xBF030000 to 0xBF030FFF
============================================
Ralink UBoot Version: 3.3
--------------------------------------------
ASIC 3052_MP2 (Port5<->None)
DRAM component: 256 Mbits SDR
DRAM bus: 16 bit
Total memory: 32 MBytes
Flash component: NOR Flash
Date:Dec  8 2009  Time:13:38:58
============================================
icache: sets:256, ways:4, linesz:32 ,total:32768
dcache: sets:128, ways:4, linesz:32 ,total:16384

 ##### The CPU freq = 320 MHZ ####

SDRAM bus set to 16 bit
 SDRAM size =32 Mbytes

Please choose the operation:
   1: Load system code to SDRAM via TFTP.
   2: Load system code then write to Flash via TFTP.
   3: Boot system code via Flash (default).
   4: Entr boot command line interface.
   9: Load Boot Loader code then write to Flash via TFTP.

You choosed 2
                                                                                                                                                                                                       0



2: System Load Linux Kernel then write to Flash via TFTP.
 Warning!! Erase Linux in Flash then burn new one. Are you sure?(Y/N)
 Please Input new ones /or Ctrl-C to discard
        Input device IP (10.10.10.199) ==:10.10.10.199
        Input server IP (10.10.10.118) ==:10.10.10.118
        Input Linux Kernel filename (firmware.bin) ==:firmware.bin

 netboot_common, argc= 3

 NetTxPacket = 0x81FE5880

 KSEG1ADDR(NetTxPacket) = 0xA1FE5880

 NetLoop,call eth_halt !

 NetLoop,call eth_init !
Trying Eth0 (10/100-M)

 Waitting for RX_DMA_BUSY status Start... done

 Header Payload scatter function is Disable !!

 ETH_STATE_ACTIVE!!
Using Eth0 (10/100-M) device
TFTP from server 10.10.10.118; our IP address is 10.10.10.199
Filename 'firmware.bin'.

 TIMEOUT_COUNT=10,Load address: 0x80100000
Loading: Got ARP REPLY, set server/gtwy eth addr (7c:c3:a1:89:8f:b8)
Got it
T #
 first block received
################################################################
         #################################################################
         #################################################################
         #################################################################
         #################################################################
         #################################################################
         #################################################################
         #################################################################
         #################################################################
         #################################################################
         #################################################################
         ####
done
Bytes transferred = 3677444 (381d04 hex)
NetBootFileXferSize= 00381d04
Erase linux kernel block !!
From 0xBF050000 To 0xBF3DFFFF

 b_end =BF3FFFFF
Erase Flash from 0xbf050000 to 0xbf3dffff in Bank # 1

 erase sector  = 12
sect = 12,s_last = 68,erase poll = 736236

 erase sector  = 13
sect = 13,s_last = 68,erase poll = 750658

 erase sector  = 14
*sect = 14,s_last = 68,erase poll = 753412

 erase sector  = 15
sect = 15,s_last = 68,erase poll = 746863

 erase sector  = 16
sect = 16,s_last = 68,erase poll = 763999

 erase sector  = 17
*sect = 17,s_last = 68,erase poll = 753723

 erase sector  = 18
sect = 18,s_last = 68,erase poll = 753707

 erase sector  = 19
sect = 19,s_last = 68,erase poll = 726721

 erase sector  = 20
*sect = 20,s_last = 68,erase poll = 752748

 erase sector  = 21
sect = 21,s_last = 68,erase poll = 735946

 erase sector  = 22
sect = 22,s_last = 68,erase poll = 755911

 erase sector  = 23
*sect = 23,s_last = 68,erase poll = 753934

 erase sector  = 24
sect = 24,s_last = 68,erase poll = 773435

 erase sector  = 25
*sect = 25,s_last = 68,erase poll = 775082

 erase sector  = 26
sect = 26,s_last = 68,erase poll = 789154

 erase sector  = 27
sect = 27,s_last = 68,erase poll = 775899

 erase sector  = 28
*sect = 28,s_last = 68,erase poll = 727306

 erase sector  = 29
sect = 29,s_last = 68,erase poll = 748463

 erase sector  = 30
sect = 30,s_last = 68,erase poll = 759573

 erase sector  = 31
*sect = 31,s_last = 68,erase poll = 765964

 erase sector  = 32
sect = 32,s_last = 68,erase poll = 773746

 erase sector  = 33
*sect = 33,s_last = 68,erase poll = 767310

 erase sector  = 34
sect = 34,s_last = 68,erase poll = 754705

 erase sector  = 35
sect = 35,s_last = 68,erase poll = 804570

 erase sector  = 36
*sect = 36,s_last = 68,erase poll = 736087

 erase sector  = 37
sect = 37,s_last = 68,erase poll = 757012

 erase sector  = 38
sect = 38,s_last = 68,erase poll = 774183

 erase sector  = 39
*sect = 39,s_last = 68,erase poll = 755389

 erase sector  = 40
sect = 40,s_last = 68,erase poll = 756933

 erase sector  = 41
sect = 41,s_last = 68,erase poll = 761290

 erase sector  = 42
*sect = 42,s_last = 68,erase poll = 760942

 erase sector  = 43
sect = 43,s_last = 68,erase poll = 744020

 erase sector  = 44
*sect = 44,s_last = 68,erase poll = 748714

 erase sector  = 45
sect = 45,s_last = 68,erase poll = 718797

 erase sector  = 46
sect = 46,s_last = 68,erase poll = 767345

 erase sector  = 47
*sect = 47,s_last = 68,erase poll = 754464

 erase sector  = 48
sect = 48,s_last = 68,erase poll = 770107

 erase sector  = 49
sect = 49,s_last = 68,erase poll = 763218

 erase sector  = 50
*sect = 50,s_last = 68,erase poll = 763802

 erase sector  = 51
sect = 51,s_last = 68,erase poll = 738284

 erase sector  = 52
sect = 52,s_last = 68,erase poll = 745649

 erase sector  = 53
*sect = 53,s_last = 68,erase poll = 726890

 erase sector  = 54
sect = 54,s_last = 68,erase poll = 736200

 erase sector  = 55
*sect = 55,s_last = 68,erase poll = 759905

 erase sector  = 56
sect = 56,s_last = 68,erase poll = 765460

 erase sector  = 57
sect = 57,s_last = 68,erase poll = 779484

 erase sector  = 58
*sect = 58,s_last = 68,erase poll = 755544

 erase sector  = 59
sect = 59,s_last = 68,erase poll = 727400

 erase sector  = 60
sect = 60,s_last = 68,erase poll = 717976

 erase sector  = 61
*sect = 61,s_last = 68,erase poll = 728772

 erase sector  = 62
sect = 62,s_last = 68,erase poll = 776409

 erase sector  = 63
sect = 63,s_last = 68,erase poll = 754066

 erase sector  = 64
*sect = 64,s_last = 68,erase poll = 764387

 erase sector  = 65
sect = 65,s_last = 68,erase poll = 772154

 erase sector  = 66
*sect = 66,s_last = 68,erase poll = 773493

 erase sector  = 67
sect = 67,s_last = 68,erase poll = 763165

 erase sector  = 68
sect = 68,s_last = 68,erase poll = 735964
 done
Erased 57 sectors

 Copy linux image[3677444 byte] to Flash[0xBF050000]....
Copy to Flash...
 Copy 3677444 byte to Flash...
 addr = 0xBF0B28A4 ,cnt=3273824
 addr = 0xBF11514A ,cnt=2870202
 addr = 0xBF1779F0 ,cnt=2466580
 addr = 0xBF1DA296 ,cnt=2062958
 addr = 0xBF23CB3C ,cnt=1659336
 addr = 0xBF29F3E2 ,cnt=1255714
 addr = 0xBF301C88 ,cnt=852092
 addr = 0xBF36452E ,cnt=448470
 addr = 0xBF3C6DD4 ,cnt=44848 done
## Booting image at bf050000 ...
   Image Name:   DD-WRT v24 Linux Kernel Image
   Created:      2009-07-18  18:25:04 UTC
   Image Type:   MIPS Linux Kernel Image (lzma compressed)
   Data Size:    856958 Bytes = 836.9 kB
   Load Address: 80000000
   Entry Point:  80267000
   Verifying Checksum ... OK
   Uncompressing Kernel Image ... OK
No initrd
## Transferring control to Linux (at address 80267000) ...
## Giving linux memsize in MB, 32

Starting kernel ...


LINUX started...

 THIS IS ASIC
Linux version 2.6.23.17 (root@dd-wrt) (gcc version 4.1.2) #572 Sat Jul 18 20:20:57 CEST 2009

 The CPU frequency set to 320 MHz
32M RAM Detected!
CPU revision is: 0001964c
Determined physical RAM map:
 memory: 02000000 @ 00000000 (usable)
Built 1 zonelists in Zone order.  Total pages: 8128
Kernel command line: console=ttyS1,57600n8 root=/dev/mtdblock4 rootfstype=squashfs noinitrd
Primary instruction cache 32kB, physically tagged, 4-way, linesize 32 bytes.
Primary data cache 16kB, 4-way, linesize 32 bytes.
Synthesized TLB refill handler (20 instructions).
Synthesized TLB load handler fastpath (32 instructions).
Synthesized TLB store handler fastpath (32 instructions).
Synthesized TLB modify handler fastpath (31 instructions).
Cache parity protection disabled
cause = 800060, status = 1100ff00
PID hash table entries: 128 (order: 7, 512 bytes)
calculating r4koff... 0030d400(3200000)
CPU frequency 320.00 MHz
Using 160.000 MHz high precision timer.
console [ttyS1] enabled
Dentry cache hash table entries: 4096 (order: 2, 16384 bytes)
Inode-cache hash table entries: 2048 (order: 1, 8192 bytes)
Memory: 29504k/32768k available (2141k kernel code, 3264k reserved, 315k data, 120k init, 0k highmem)
Mount-cache hash table entries: 512
NET: Registered protocol family 16
Generic PHY: Registered new driver
NET: Registered protocol family 2
Time: MIPS clocksource has been installed.
IP route cache hash table entries: 1024 (order: 0, 4096 bytes)
TCP established hash table entries: 1024 (order: 1, 8192 bytes)
TCP bind hash table entries: 1024 (order: 0, 4096 bytes)
TCP: Hash tables configured (established 1024 bind 1024)
TCP reno registered
Load RT2880 Timer Module(Wdg/Soft)
devfs: 2004-01-31 Richard Gooch (rgooch@atnf.csiro.au)
devfs: boot_options: 0x1
squashfs: version 3.0 (2006/03/15) Phillip Lougher
io scheduler noop registered
io scheduler deadline registered (default)
Ralink gpio driver initialized
Serial: 8250/16550 driver $Revision: 1.3 $ 2 ports, IRQ sharing disabled
serial8250: ttyS0 at I/O 0xb0000500 (irq = 37) is a 16550A
serial8250: ttyS1 at I/O 0xb0000c00 (irq = 12) is a 16550A
PPP generic driver version 2.4.2
PPP Deflate Compression module registered
PPP BSD Compression module registered
MPPE/MPPC encryption/compression module registered
NET: Registered protocol family 24
tun: Universal TUN/TAP device driver, 1.6
tun: (C) 1999-2004 Max Krasnyansky <maxk@qualcomm.com>
ralink flash device: 0x800000 at 0xbf000000
Ralink SoC physically mapped flash: Found 1 x16 devices at 0x0 in 16-bit bank
 Amd/Fujitsu Extended Query Table at 0x0040
number of CFI chips: 1
cfi_cmdset_0002: Disabling erase-suspend-program due to code brokenness.

found squashfs at 122000
Creating 6 MTD partitions on "Ralink SoC physically mapped flash":
0x00000000-0x00030000 : "uboot"
0x00030000-0x00040000 : "uboot-config"
0x00040000-0x00050000 : "factory-defaults"
0x00050000-0x003f0000 : "linux"
0x00122000-0x003f0000 : "rootfs"
mtd: partition "rootfs" doesn't start on an erase block boundary -- force read-only
0x003f0000-0x00400000 : "nvram"
u32 classifier
    Actions configured
Netfilter messages via NETLINK v0.30.
nf_conntrack version 0.5.0 (1024 buckets, 4096 max)
ctnetlink v0.93: registering with nfnetlink.
IPv4 over IPv4 tunneling driver
GRE over IPv4 tunneling driver
ip_tables: (C) 2000-2006 Netfilter Core Team
IPP2P v0.8.2 loading
ClusterIP Version 0.8 loaded successfully
TCP bic registered
TCP cubic registered
TCP westwood registered
TCP highspeed registered
TCP hybla registered
TCP htcp registered
TCP vegas registered
TCP scalable registered
NET: Registered protocol family 1
NET: Registered protocol family 17
Welcome to PF_RING 3.2.1
(C) 2004-06 L.Deri <deri@ntop.org>
NET: Registered protocol family 27
PF_RING: bucket length    128 bytes
PF_RING: ring slots       4096
PF_RING: sample rate      1 [1=no sampling]
PF_RING: capture TX       No [RX only]
PF_RING: transparent mode Yes
PF_RING initialized correctly.
PF_RING: registered /proc/net/pf_ring/
802.1Q VLAN Support v1.8 Ben Greear <greearb@candelatech.com>
All bugs added by David S. Miller <davem@redhat.com>
GDMA1_MAC_ADRH -- : 0x00000000
GDMA1_MAC_ADRL -- : 0x00000000
Ralink APSoC Ethernet Driver Initilization. v2.00  256 rx/tx descriptors allocated, mtu = 1500!
NAPI enable, weight = 0, Tx Ring = 256, Rx Ring = 256
GDMA1_MAC_ADRH -- : 0x0000000c
GDMA1_MAC_ADRL -- : 0x43305277
PROC INIT OK!
decode /dev/mtdblock4
VFS: Mounted root (squashfs filesystem) readonly.
Mounted devfs on /dev
Freeing unused kernel memory: 120k freed
starting Architecture code for rt2880
rt2860v2_ap: module license 'unspecified' taints kernel.

phy_tx_ring = 0x01c43000, tx_ring = 0xa1c43000, size: 16 bytes

phy_rx_ring = 0x01c44000, rx_ring = 0xa1c44000, size: 16 bytes
RT305x_ESW: Link Status Changed
GDMA1_FWD_CFG = 10000
switch reg write offset=14, value=405555
switch reg write offset=50, value=2001
switch reg write offset=98, value=7f3f
switch reg write offset=e4, value=3f
switch reg write offset=40, value=1001
switch reg write offset=44, value=1001
switch reg write offset=48, value=1002
switch reg write offset=70, value=ffff506f
br0: Dropping NETIF_F_UFO since no NETIF_F_HW_CSUM feature.
Algorithmics/MIPS FPU Emulator v1.5
device vlan1 entered promiscuous mode
device eth2 entered promiscuous mode
RtmpOSNetDevDetach(): RtmpOSNetDeviceDetach(), dev->name=ra0!
0x1300 = 00064380
Terminate the task(RtmpWscTask) with pid(726)!
0x1300 = 00064380
device ra0 entered promiscuous mode
br0: port 2(ra0) entering learning state
br0: port 1(vlan1) entering learning state
wland: No such file or directory
device vlan2 entered promiscuous mode
device vlan2 left promiscuous mode
device vlan2 entered promiscuous mode
br0: topology change detected, propagating
br0: port 2(ra0) entering forwarding state
br0: topology change detected, propagating
br0: port 1(vlan1) entering forwarding state
SIOCGIFFLAGS: No such device
device br0 entered promiscuous mode
SIOCGIFFLAGS: No such device
SIOCGIFFLAGS: No such device
etherip: Ethernet over IPv4 tunneling driver
nvram was changed, needs commit, waiting 10 sec.
SIOCGIFFLAGS: No such device
SIOCGIFFLAGS: No such device
SIOCGIFFLAGS: No such device
SIOCGIFFLAGS: No such device
nvram_commit(): end

DD-WRT v24-sp2 std (c) 2009 NewMedia-NET GmbH
Release: 07/18/09 (SVN revision: 12524)
▒
DD-WRT login:
```

</details>

Default credentials:
* Username: root
* Password: admin

### Credits
Thank you to the fine folks here: https://forum.dd-wrt.com/phpBB2/viewtopic.php?t=70848




## Install OpenWrt
The procedure will be the same as with dd-wrt, using the tftp server and the serial console. You will need to flash the image marked squashfs-tftp that you find on this repository.

I custom-built it from [openwrt repo](https://git.openwrt.org/openwrt/openwrt.git), branch *openwrt-19.07* with the *c300.config* you find on this repo.
I needed to remove something otherwise there would be no space on the flash for the overlay (i.e. no space for persistent settings, which sucks). Among the stuff I removed ppp, usb, mkswap, awk. You may want to re-insert awk, I noticed that it is needed for something, but I guess it is not crucial.

If you get a message like [jffs2: Too few erase blocks (1)](https://www.olimex.com/forum/index.php?topic=4527.0) it means that the image is too large.
