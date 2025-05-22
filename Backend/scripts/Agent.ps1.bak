param (
    [string]$ServerUrl = "http://0.0.0.0/upload",
    [string]$ProjectName = "New Project",
    [string]$scan_ip
)

if ($ServerUrl -ne "http://0.0.0.0/upload" ) {

    $cs = Get-CimInstance Win32_ComputerSystem
    $compInfo = Get-ComputerInfo

    function Is-ValidIP($address) {
        return [System.Net.IPAddress]::TryParse($address, [ref]$null)
    }
    function Get-ScanIP {
        
        try {
            $uri = [System.Uri]$ServerUrl
        } catch {
            throw "Invalid URL format: '$Url'"
        }

        # Determine port (handle default cases)
        $port = if ($uri.IsDefaultPort) {
            if ($uri.Scheme -eq "https") { 443 } else { 80 }
        } else {
            $uri.Port
        }

        $targetHost = $uri.Host  # Rename $host to $targetHost

        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $tcpClient.Connect($targetHost, $port)
            $localIP = $tcpClient.Client.LocalEndPoint.Address.ToString()
            $tcpClient.Close()
            return $localIP
        } catch {
            $msg = "Could not connect to $targetHost on port $port. Error: " + $_.Exception.Message
            throw $msg
        }
    }

    # Helper Functions
    function Get-PhysicalIPAddress {
        (Get-NetAdapter |
            Where-Object { $_.Status -eq "Up" -and $_.HardwareInterface -eq $true -and $_.InterfaceDescription -notmatch "Virtual|VMware|Hyper-V|VPN|Loopback|Docker" } |
            ForEach-Object {
                Get-NetIPAddress -InterfaceIndex $_.InterfaceIndex -AddressFamily IPv4
            } |
            Where-Object { $_.IPAddress } |
            Select-Object -ExpandProperty IPAddress -First 1)
    }

    function Get-PhysicalMacAddress {
        (Get-NetAdapter |
            Where-Object { $_.Status -eq "Up" -and $_.HardwareInterface -eq $true -and $_.InterfaceDescription -notmatch "Virtual|VMware|Hyper-V|VPN|Loopback|Docker" } |
            Select-Object -ExpandProperty MacAddress -First 1)
    }

    function Get-WindowsLicenseInfo {
        $licenseInfo = [ordered]@{
            LicenseType   = "Unknown"
            LicenseStatus = "Unknown"
        }

        try {
            # Run the slmgr.vbs command to get license info
            $output = cscript.exe /nologo "$env:SystemRoot\System32\slmgr.vbs" /dli 2>&1

            # Split the output by newlines
            $lines = $output -split "`n"

            # Loop through each line and match the relevant information
            foreach ($line in $lines) {
                if ($line -match "Description:\s+(.+)") {
                    $licenseInfo["LicenseType"] = $matches[1].Trim()
                }
                if ($line -match "License Status:\s+(.+)") {
                    $licenseInfo["LicenseStatus"] = $matches[1].Trim()
                }
            }
        } catch {
            # Error handling with more details
            $licenseInfo["LicenseType"] = "Error"
            $licenseInfo["LicenseStatus"] = "Error"
        }

        return $licenseInfo
    }

    function Decode-ProductState {
        param([int]$state)
        $hex = "{0:X6}" -f $state
        [ordered]@{
            HexValue        = $hex
            RealTimeStatus  = if ($hex[1] -eq '1') {'On'} else {'Off'}
            AVEnabled       = if ($hex[0] -in '1','2','4','6') {'Enabled'} else {'Disabled'}
            SignatureStatus = if ($hex[2] -eq '0') {'Up-to-date'} else {'Outdated'}
        }
    }

    function Get-DefenderStatus {
        try {
            $status = Get-MpComputerStatus
            $defenderInfo = [ordered]@{
                Name                        = "Windows Defender"
                AntivirusEnabled            = if ($status.AntivirusEnabled) { "Enabled" } else { "Disabled" }
                "AV Signature Last Update"  = $status.AntivirusSignatureLastUpdated.ToString()
                AntivirusSignatureVersion   = $status.AntivirusSignatureVersion
                RealTime                    = if ($status.RealTimeProtectionEnabled) { "On" } else { "Off" }
                SignatureStatus             = if ($status.AntivirusSignatureAge -eq 0) { "Up-to-date" } else { "Outdated" }
                IsTamperProtected           = $status.IsTamperProtected
                BehaviorMonitorEnabled      = $status.BehaviorMonitorEnabled
                AMServiceEnabled            = $status.AMServiceEnabled
                AMServiceVersion            = $status.AMServiceVersion
                AntispywareEnabled          = $status.AntispywareEnabled
            }
            return $defenderInfo
        } catch {
            Write-Error "Windows Defender may not be installed or accessible."
            return $null
        }
    }


    function Get-AntiVirusStatus {
        $avProducts = @()
        try {
            $products = Get-CimInstance -Namespace "root/SecurityCenter2" -ClassName AntiVirusProduct -ErrorAction Stop
            foreach ($product in $products) {
                if ($product.displayName -like "*Defender*") {
                    $defender = Get-DefenderStatus
                    if ($defender) { $avProducts += $defender }
                } else {
                    $decoded = Decode-ProductState -state $product.productState
                    $avProducts += [ordered]@{
                        Name            = $product.displayName
                        Enabled         = $decoded.AVEnabled
                        RealTime        = $decoded.RealTimeStatus
                        SignatureStatus = $decoded.SignatureStatus
                    }
                }
            }
        } catch {
            Write-Warning "SecurityCenter2 not available. Trying Get-MpComputerStatus..."
            $defender = Get-DefenderStatus
            if ($defender) { $avProducts += $defender }
        }
        return $avProducts
    }

    function Get-FirewallStatus {
        Get-NetFirewallProfile | ForEach-Object {
            [ordered]@{
                Profile              = $_.Name
                Enabled              = if ($_.Enabled) { "Enabled" } else { "Disabled" }
                DefaultInboundAction = if ($_.DefaultInboundAction -eq 0) { "Allow" } else { "Block" }
                DefaultOutboundAction = if ($_.DefaultOutboundAction -eq 0) { "Allow" } else { "Block" }
            }
        }
    }

    function Get-PatchUpdates {
        Get-HotFix | ForEach-Object {
            [ordered]@{
                Description = $_.Description
                InstalledOn = if ($_.InstalledOn) { $_.InstalledOn.ToString("yyyy-MM-dd") } else { "Unknown" }
                HotFixID    = $_.HotFixID
            }
        }
    }

    function Get-WindowsLicenseInfo {
        [CmdletBinding()]
        param ()

        # Ordered flat output object
        $licenseData = [ordered]@{
            Name               = "Unknown"
            Description        = "Unknown"
            LicenseType        = "Unknown"
            LicenseStatus      = "Unknown"
            ActivationStatus   = "Unknown"
            ActivationMessage  = "No activation status information available."
            OEMProductKey      = "Not Found"
        }

        try {
            $dliOutput = cscript.exe /nologo "$env:SystemRoot\System32\slmgr.vbs" /dli 2>&1
            $dliLines = $dliOutput -split "`n"

            foreach ($line in $dliLines) {
                if ($line -match '^Name:\s+(.+)') {
                    $licenseData.Name = $matches[1].Trim()
                }
                elseif ($line -match '^Description:\s+(.+)') {
                    $licenseData.Description = $matches[1].Trim()
                    $licenseData.LicenseType = $matches[1].Trim()
                }
                elseif ($line -match '^License Status:\s+(.+)') {
                    $licenseData.LicenseStatus = $matches[1].Trim()
                }
            }
        } catch {
            $licenseData.LicenseStatus = "Error"
            $licenseData.LicenseType   = "Error"
        }

        try {
            $xprOutput = cscript.exe /nologo "$env:SystemRoot\System32\slmgr.vbs" /xpr 2>&1
            if ($xprOutput) {
                $activationLine = $xprOutput | Where-Object { $_ -match 'activated|will expire' }
                if ($activationLine) {
                    $licenseData.ActivationStatus = if ($activationLine -match 'permanently activated') { "Permanent" } else { "Temporary" }
                    $licenseData.ActivationMessage = $activationLine.Trim()
                }
            }
        } catch {
            $licenseData.ActivationStatus  = "Error"
            $licenseData.ActivationMessage = "Error retrieving activation status."
        }

        try {
            $oemKey = (Get-CimInstance -Query 'SELECT * FROM SoftwareLicensingService').OA3xOriginalProductKey
            if ($oemKey) {
                $licenseData.OEMProductKey = $oemKey
            }
        } catch {
            $licenseData.OEMProductKey = "Error"
        }

        return $licenseData # | ConvertTo-Json -Depth 2
    }

    function Get-GPUInfo {
        [CmdletBinding()]
        param ()

        try {
            $gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1

            $gpuInfo = @(
                [ordered]@{
                    Name           = $gpu.Name
                    VideoProcessor = $gpu.VideoProcessor
                    DriverVersion  = $gpu.DriverVersion
                    AdapterRAMGB   = if ($gpu.AdapterRAM) { "{0:N2}" -f ($gpu.AdapterRAM / 1GB) } else { "N/A" }
                    }
            )

            return $gpuInfo
        } catch {
            return false
        }
    }

    function Get-UserInfo {
        $Users = Get-CimInstance Win32_UserAccount | ForEach-Object {
            [ordered]@{
                Name                = $_.Name
                SID                 = $_.SID
                Domain              = if ($_.LocalAccount -eq $false) { $_.Domain } else { "" }
                IsActive            = -not $_.Disabled
                IsLockout           = $_.Lockout
                IsPasswordRequired  = $_.PasswordRequired
                IsLocalAccount      = $_.LocalAccount
            }
        }

        return $Users # | ConvertTo-Json -Depth 3
    }

    function Get-KeyboardInfo {
        $keyboards = Get-CimInstance Win32_Keyboard

        if ($keyboards.Count -eq 0) {
            return false 
        }

        $keyboardInfo = $keyboards | ForEach-Object {
            [ordered]@{
                Name        = $_.Name
                Description = $_.Description
                DeviceID    = $_.DeviceID
            }
        }

        return $keyboardInfo # | ConvertTo-Json -Depth 3
    }

    function Get-MouseInfo {
        $mice = Get-CimInstance Win32_PointingDevice

        if ($mice.Count -eq 0) {
            return ConvertTo-Json @("No mouse detected.")
        }

        $mouseInfo = $mice | ForEach-Object {
            [ordered]@{
                Name        = $_.Name
                Description = $_.Description
                DeviceID    = $_.DeviceID
                PNPDeviceID = $_.PNPDeviceID
                #Status      = $_.Status
                Manufacturer= $_.Manufacturer
                #NumberOfButtons = $_.NumberOfButtons
            }
        }

        return $mouseInfo # | ConvertTo-Json -Depth 3
    }

    function Get-InstalledSoftware {
        $Software32 = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* `
                    | Where-Object { $_.DisplayName } `
                    | Select-Object DisplayName, DisplayVersion

        $Software64 = Get-ItemProperty HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* `
                    | Where-Object { $_.DisplayName } `
                    | Select-Object DisplayName, DisplayVersion

        $SoftwareSet = @{}

        foreach ($item in ($Software32 + $Software64)) {
            if (-not $SoftwareSet.ContainsKey($item.DisplayName)) {
                $SoftwareSet[$item.DisplayName] = [ordered]@{
                    Name    = $item.DisplayName
                    Version = $item.DisplayVersion
                }
            }
        }

        return $SoftwareSet.Values
    }

    function Get-DomainRoleName {
        # $compInfo = Get-ComputerInfo 
        $domainRoleMap = @{
            0 = "Standalone Workstation"
            1 = "Member Workstation"
            2 = "Standalone Server"
            3 = "Member Server"
            4 = "Backup Domain Controller"
            5 = "Primary Domain Controller"
        }

        $roleValue = [int]$compInfo.CsDomainRole  # Force cast to int

        if ($domainRoleMap.ContainsKey($roleValue)) {
            return $domainRoleMap[$roleValue]
        } else {
            return "Unknown ($roleValue)"
        }
    }

    function Get-LogicalDiskInfo {
        try {
            $driveTypeMap = @{
                0 = "Unknown"
                1 = "No Root Directory"
                2 = "Removable Disk"
                3 = "Local Disk"
                4 = "Network Drive"
                5 = "Compact Disc"
                6 = "RAM Disk"
            }

            $logicalDisks = Get-CimInstance Win32_LogicalDisk
            $result = $logicalDisks | ForEach-Object {
                $driveTypeValue = [int]$_.DriveType  # Explicit cast to int
                $mappedType = if ($driveTypeMap.ContainsKey($driveTypeValue)) {
                    $driveTypeMap[$driveTypeValue]
                } else {
                    "Unknown"
                }

                [ordered]@{
                    DeviceID            = $_.DeviceID
                    VolumeName          = $_.VolumeName
                    FileSystem          = $_.FileSystem
                    DriveType           = $mappedType
                    SerialNumber        = $_.VolumeSerialNumber
                    HardDiskCapacityGB  = if ($_.Size) { [math]::Round($_.Size / 1GB, 2) } else { "N/A" }
                    FreeSpaceGB         = if ($_.FreeSpace) { [math]::Round($_.FreeSpace / 1GB, 2) } else { "N/A" }
                }
            }

            return $result
        } catch {
            Write-Error "Failed to get logical disk info: $_"
        }
    }

    function Get-PhysicalDriveInfo {
        try {
            $hardDisks = Get-CimInstance Win32_DiskDrive

            $hardDisks | ForEach-Object {
                [ordered]@{
                    DriveID   = ($_.DeviceID -replace "^\\\\\.\\", "")
                    DriveType = if ($_.MediaType) { $_.MediaType } else { "Unknown" }
                    Model     = $_.Model
                    SizeGB    = "{0:N2}" -f ($_.Size / 1GB)
                }
            }
        } catch {
            Write-Error "Failed to get physical drive info: $_"
        }
    }

    function Get-NetworkAdapterInfo {
        try {
            # Get adapters with IP enabled
            $cimAdapters = Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled }
            $netAdapters = Get-NetAdapter

            $adapterInfo = foreach ($cim in $cimAdapters) {
                $matchingNetAdapter = $netAdapters | Where-Object { $_.MacAddress -replace '-', ':' -eq $cim.MACAddress.ToUpper() }

                $ipInfo = @()
                if ($matchingNetAdapter) {
                    $ipInfo = Get-NetIPAddress -InterfaceIndex $matchingNetAdapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
                }

                [ordered]@{
                    NICName       = $cim.Description
                    IPv4Addresses = ($ipInfo | Select-Object -ExpandProperty IPAddress) -join ", "
                    MACAddress    = $cim.MACAddress
                    DHCP          = $cim.DHCPEnabled
                    DHCPServer    = if ($cim.DHCPServer) { $cim.DHCPServer } else { "N/A" }
                    Network       = $cim.DNSDomain
                }
            }

            return $adapterInfo
        } catch {
            Write-Error "Failed to get network adapter info: $_"
        }
    }

    function Get-ProcessorInfo {
        try {
            $processors = Get-CimInstance Win32_Processor

            $processors | ForEach-Object {
                [ordered]@{
                    DeviceID              = $_.DeviceID
                    ProcessorName         = $_.Name
                    ProcessorManufacturer = $_.Manufacturer
                    ProcessorSpeedInGHz   = "{0:N2}" -f ($_.MaxClockSpeed / 1000)
                    NumberOfCores         = $_.NumberOfCores
                    NumberOfThreads       = $_.NumberOfLogicalProcessors
                }
            }
        } catch {
            Write-Error "Failed to get processor info: $_"
        }
    }



    # Asset Details
    
    $ip = Get-PhysicalIPAddress
    $mac = Get-PhysicalMacAddress
    
    # RAM
    $ramsize = [math]::Round($compInfo.CsPhyicallyInstalledMemory / 1048576, 2)
    
    $AvaiRAM  = [math]::Round($compInfo.OsTotalVisibleMemorySize / 1048576, 2)
    $freeRAM  = [math]::Round($compInfo.OsFreePhysicalMemory / 1048576, 2)
    $usedRAM  = $AvaiRAM - $freeRAM
    
    $gpu = Get-GPUInfo
    # $gpuRam = if ($gpu.AdapterRAM) { "{0:0}" -f ($gpu.AdapterRAM / 1GB) } else { "Unknown" }

    # Procesor Details
    $proc = Get-CimInstance Win32_Processor | Select-Object -First 1
    # Disk Details

    $diskSize = [math]::Round((Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Measure-Object -Property Size -Sum).Sum / 1GB)

    # Hardware Details

    #$hardDisks = Get-CimInstance Win32_DiskDrive
    #$networkAdapters = Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled }


    $clientip = if ($scan_ip) { if (Is-ValidIP $scan_ip) { $scan_ip } else { Write-Error "Invalid IP address provided: $scan_ip"; exit 1 } } else { $scan_ip = Get-ScanIP; $scan_ip } #Get-ScanIP

    $AssetProjectDetails = [ordered]@{
        ProjectName         = $ProjectName
        ClientIp            = $clientip
        MachineName         = $compInfo.CsName

    }

    
    $AssetDetails = [ordered]@{
        SystemName          = $compInfo.CsName
        SystemManufacturer  = $compInfo.CsManufacturer
        SystemModel         = $compInfo.CsModel
        SystemType          = $compInfo.CsSystemType
        SystemSKU           = $compInfo.CsSystemSKUNumber
        DiskSpaceGB         = $diskSize
        "Ram Size"          = $ramsize
        GPU                 = $gpu.AdapterRAMGB
        OperatingSystem     = $compInfo.OsName
        IPAddress           = $ip
        MacAddress          = $mac
        Domain              = $compInfo.CsDomain
        "Domain Role"       = Get-DomainRoleName
        WorkGroup           = $compInfo.Csworkgroup
        LicenseStatus       = $license.LicenseStatus
        LoggedInUser        = $env:USERNAME
    }

    $Users = Get-UserInfo

    $Hardware = @(
        [ordered]@{
            ComputerSystem = [ordered]@{
                SystemName          = $compInfo.CsName
                SystemManufacturer  = $compInfo.CsManufacturer
                SystemModel         = $compInfo.CsModel
                SystemType          = $compInfo.CsSystemType
                SystemSKU           = $compInfo.CsSystemSKUNumber
                "BIOS Name"         = $compInfo.BiosName 
                "Bios Manufacturer"     = $compInfo.BiosManufacturer
                "SMBIOSBIOSVersion"     = $compInfo.BiosSMBIOSBIOSVersion
                "SMBiosVersion"         = $compInfo.BiosSMBIOSMajorVersion
                "BIOS Serial Number"    = $compInfo.BiosSeralNumber
                "BIOS Release Date"     = $compInfo.BiosReleaseDate.ToString() # $bios.ReleaseDate.ToString("yyyy-MM-dd")
            }
        },
        [ordered]@{
            OperatingSystem = [ordered]@{
                "Operating System" = $compInfo.OsName
                "OS Architecture"   = $compInfo.OsArchitecture 
                OSVersion       = $compInfo.OsVersion
                BuildNumber     = $compInfo.OsBuildNumber
                ProductID       = $compInfo.WindowsProductId
                "OS Product Type"   = $compInfo.OsProductType
                "Os System Directory"   = $compInfo.OsSystemDirectory
                "Os System Drive"   = $compInfo.OsSystemDrive
                "Os Windows Directory"  = $compInfo.OsWindowsDirectory
                
            }
        },
        [ordered]@{
            License = Get-WindowsLicenseInfo
        },
        [ordered]@{
            Processor = Get-ProcessorInfo
        },
        [ordered]@{
            Ram = [ordered]@{
                "Installed RAM" = $ramsize
                "Available RAM" = $AvaiRAM
                "Used"          = $usedRAM
                "Free"          = $freeRAM
            }
        },
        [ordered]@{
            VRam = [ordered]@{
                TotalVirtualMemoryGB    = "{0:N2}" -f ($compInfo.OsTotalVirtualMemorySize / 1MB)
                FreeVirtualMemoryGB     = "{0:N2}" -f ($compInfo.OsFreeVirtualMemory / 1MB)
                InUseVirtualMemoryGB    = "{0:N2}" -f ($compInfo.OsInUseVirtualMemory / 1MB)
            }
        },
        [ordered]@{
            GPU = $gpu
        },
        [ordered]@{
            NetworkAdapters = Get-NetworkAdapterInfo
        },
        [ordered]@{
            PhysicalDrives = Get-PhysicalDriveInfo
        },
        [ordered]@{
            logicalDiskVolume = Get-LogicalDiskInfo
        },
        [ordered]@{
            keyboard = Get-keyboardInfo
        },
        [ordered]@{
            Mouse = Get-MouseInfo
        }
    )

    # Software
    $Software = Get-InstalledSoftware

    # Security
    $Security = @(
        [ordered]@{
            Antivirus = Get-AntiVirusStatus
        },
        [ordered]@{
            Firewall = Get-FirewallStatus
        },
        [ordered]@{
            AntiPatchUpdatesvirus = Get-PatchUpdates
        }
    )
    

    # Final JSON
    $data = [ordered]@{
        AssetProjectDetails    = $AssetProjectDetails
        AssetDetails = $AssetDetails
        Users        = $Users
        Hardware     = $Hardware
        Software     = $Software
        Security     = $Security
    }

    $json = $data | ConvertTo-Json -Depth 10
    try{
        
        Invoke-RestMethod -Uri $ServerUrl -Method Post -Body $json -ContentType "application/json"
        # Write-Host "`nResponse Status Code: $($response.StatusCode)"
    } catch{
        $date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
        $outfile = "C:\Windows\Temp\report_$date.json"
        Out-File -FilePath $outfile -InputObject $json
        Write-Output @"
[*] Can't able to reach the server: $ServerUrl
[*] Report File: $outfile
[*] Error Details: $($_.Exception.Message)
"@
    }
    
} else {
    Write-Output @"
[*] Server URL not Defined
[*] Usage:
    powershell.exe -ExecutionPolicy Bypass -File .\script-name.ps1 -ServerUrl 'http://<server-ip>/upload'
"@
}
