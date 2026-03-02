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
```
