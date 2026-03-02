# Check if Windows Is Using Hyper-V
```
PS C:\Windows\system32> systeminfo | findstr /i "hyper-v"
Hyper-V Requirements:      A hypervisor has been detected. Features required for Hyper-V will not be displayed.
```

# If You Use VMware / VirtualBox / GNS3 / EVEt, then you should disable Hyper-V
### run cmd
```
C:\Windows\System32>bcdedit /set hypervisorlaunchtype off
The operation completed successfully.
```

```
reboot pc
```

# After reboot, check again:
You should now see something like:
```
PS C:\Windows\system32> systeminfo | findstr /i "hyper-v"
Hyper-V Requirements:      VM Monitor Mode Extensions: Yes
```


# Re-enable Later (If Needed), If someday you want Hyper-V back:  
> This is needed for ContainerLab.
run cmd
```
bcdedit /set hypervisorlaunchtype auto
```


# Verify VT-x Is Available
- Should already be enabled previously via BIOS

# run wsl and verify kvm is running for the containerlab to work
```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Users\T7810> wsl
khau@DESKTOP-FTEM5HO:/mnt/c/Users/T7810$ ls -l /dev/kvm
crw-rw---- 1 root kvm 10, 232 Mar  1 12:01 /dev/kvm
khau@DESKTOP-FTEM5HO:/mnt/c/Users/T7810$

```

# To move that specific Arista cEOS image into your current Containerlab directory, run this command inside your Containerlab terminal:
Bash
```
cp "/mnt/c/Users/T7810/Downloads/cEOS-lab-4.32.0F.tar.xz" .

clab@DESKTOP-FTEM5HO:~/mycontainer-lab$ docker import cEOS-lab-4.32.0F.tar.xz ceos:4.32.0F
sha256:7a8a06ac2b33f1167c968adcd7857afa73615ff37a986d17eacc5dd7c7266184

or

clab@DESKTOP-FTEM5HO:~/mycontainer-lab$ docker import /mnt/c/Users/T7810/Downloads/cEOS-lab-4.32.0F.tar.xz ceos:4.32.0F

```
```
clab@DESKTOP-FTEM5HO:~/mycontainer-lab$ docker images
REPOSITORY                             TAG        IMAGE ID       CREATED         SIZE
ceos                                   4.32.0F    7a8a06ac2b33   2 minutes ago   2.04GB
vrnetlab/juniper_vjunos-switch         23.1R1.8   78a03da070df   2 months ago    4.45GB
alpine                                 latest     e7b39c54cdec   2 months ago    8.44MB
ghcr.io/srl-labs/clab-io-draw          latest     3c1b20095dba   5 months ago    172MB
ghcr.io/kaelemc/wireshark-vnc-docker   latest     4cebbe954b93   7 months ago    554MB
ghcr.io/siemens/ghostwire              latest     18664310d22f   19 months ago   36.5MB
ghcr.io/siemens/packetflix             latest     6bed7a0d2a95   2 years ago     122MB
```
