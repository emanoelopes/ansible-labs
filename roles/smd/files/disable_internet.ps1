param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("enable", "disable")]
    [string]$Action
)

$InterfaceName = Get-NetIPConfiguration | Where-Object {$_.IPv4DefaultGateway -ne $null} | Select-Object -ExpandProperty InterfaceAlias

if (-not $InterfaceName) {
    Write-Error "Não foi possível identificar a interface de rede conectada à internet."
    exit 1
}

if ($Action -eq "enable") {
    Write-Host "Habilitando a interface '$InterfaceName'..."
    netsh interface set interface "$InterfaceName" admin=enable
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Erro ao habilitar a interface '$InterfaceName'."
        exit 1
    }
    Write-Host "Interface '$InterfaceName' habilitada com sucesso."
} elseif ($Action -eq "disable") {
    Write-Host "Desabilitando a interface '$InterfaceName'..."
    netsh interface set interface "$InterfaceName" admin=disable
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Erro ao desabilitar a interface '$InterfaceName'."
        exit 1
    }
    Write-Host "Interface '$InterfaceName' desabilitada com sucesso."
}