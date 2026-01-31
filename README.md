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


# Re-enable Later (If Needed), If someday you want Hyper-V back:  --- neede for containerlab
run cmd
```
bcdedit /set hypervisorlaunchtype auto
```


# Verify VT-x Is Available
- should enabea alreaduy prevuouly via bios
